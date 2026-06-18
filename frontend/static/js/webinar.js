// webinar.js -- the only "smart" page.
//
// Server-clock JIT/evergreen sync: the browser asks the SERVER for the current
// time and the computed session start, then trusts the SERVER clock (not its
// own). Refreshing or changing the local clock can't cheat the offer timing.
//
// Flow: load state -> click-to-join (autoplay policy) -> YouTube IFrame seeked
// to (serverNow - sessionStart) -> timed offer CTAs reveal -> "ended" state.
//
// Exposes Alpine component `webinarRoom(audience)`.

function webinarRoom(audience) {
  return {
    audience: audience,
    loading: true,
    error: null,
    state: "loading", // loading | waiting | ready | live | ended
    joined: false,

    // synced clock
    baseServerMs: 0,
    basePerfMs: 0,

    // config from server
    title: "",
    youtubeId: "",
    durationSeconds: 0,
    sessionStartMs: 0,
    nextSessionStartMs: 0,
    courseRevealSeconds: 0,
    offerRevealSeconds: 0,
    prices: { course: "35", coaching_single: "75", coaching_package: "200" },

    // derived
    elapsed: 0,
    countdown: 0,
    progressPct: 0,
    showCourseOffer: false,
    showCoachingOffer: false,
    courseFired: false,
    coachingFired: false,

    // ticker
    tip: "",
    tipKey: 0,

    player: null,
    _tickHandle: null,
    _resyncHandle: null,
    _tipHandle: null,
    _driftHandle: null,

    syncedNowMs() {
      return this.baseServerMs + (performance.now() - this.basePerfMs);
    },

    fmt(totalSeconds) {
      totalSeconds = Math.max(0, Math.floor(totalSeconds));
      var m = Math.floor(totalSeconds / 60);
      var s = totalSeconds % 60;
      return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    },

    async init() {
      try {
        await this.loadState(true);
      } catch (e) {
        this.error = "Could not load the session. Please refresh.";
        this.loading = false;
        return;
      }
      this.loading = false;
      this.startTicker();
      this.startClocks();
      this.recompute();
      if (window.TN) window.TN.track("webinar_enter", { audience: this.audience });
    },

    async loadState(resyncBase) {
      var res = await fetch("/api/webinar/state?audience=" + encodeURIComponent(this.audience));
      if (!res.ok) throw new Error("state " + res.status);
      var d = await res.json();
      this.title = d.title;
      this.youtubeId = d.youtube_id;
      this.durationSeconds = d.duration_seconds;
      this.sessionStartMs = d.session_start_ms;
      this.nextSessionStartMs = d.next_session_start_ms;
      this.courseRevealSeconds = d.course_reveal_seconds;
      this.offerRevealSeconds = d.offer_reveal_seconds;
      this.prices = d.prices || this.prices;
      if (resyncBase) {
        this.baseServerMs = d.server_now_ms;
        this.basePerfMs = performance.now();
      }
    },

    startClocks() {
      var self = this;
      this._tickHandle = setInterval(function () { self.recompute(); }, 1000);
      // Re-sync the authoritative clock periodically (cheap /api/time call).
      this._resyncHandle = setInterval(async function () {
        try {
          var res = await fetch("/api/time");
          var d = await res.json();
          self.baseServerMs = d.server_now_ms;
          self.basePerfMs = performance.now();
        } catch (e) { /* keep existing clock */ }
      }, 30000);
    },

    recompute() {
      var nowMs = this.syncedNowMs();
      var elapsed = Math.floor((nowMs - this.sessionStartMs) / 1000);
      this.elapsed = elapsed;

      if (elapsed < 0) {
        this.state = this.joined ? "live" : "waiting";
        this.countdown = Math.abs(elapsed);
      } else if (elapsed >= this.durationSeconds) {
        this.state = "ended";
      } else {
        this.state = this.joined ? "live" : "ready";
      }

      this.progressPct = this.durationSeconds
        ? Math.min(100, Math.max(0, (elapsed / this.durationSeconds) * 100))
        : 0;

      // Timed offer reveals (server-clock based; can't be skipped by refresh).
      this.showCourseOffer = elapsed >= this.courseRevealSeconds && this.state !== "ended";
      this.showCoachingOffer = elapsed >= this.offerRevealSeconds && this.state !== "ended";

      if (this.showCourseOffer && !this.courseFired) {
        this.courseFired = true;
        if (window.TN) window.TN.track("offer_reveal", { type: "course", at: elapsed });
      }
      if (this.showCoachingOffer && !this.coachingFired) {
        this.coachingFired = true;
        if (window.TN) window.TN.track("offer_reveal", { type: "coaching", at: elapsed });
      }
    },

    // --- click-to-join (satisfies browser autoplay gesture requirement) ---
    join() {
      this.joined = true;
      if (window.TN) window.TN.track("webinar_join", { audience: this.audience, at: this.elapsed });
      this.recompute();
      this.$nextTick(() => this.mountPlayer());
    },

    mountPlayer() {
      var self = this;
      function create() {
        var startAt = Math.min(Math.max(0, self.elapsed), self.durationSeconds);
        self.player = new YT.Player("yt-player", {
          videoId: self.youtubeId,
          playerVars: {
            start: startAt,
            autoplay: 1,
            controls: 0,
            rel: 0,
            modestbranding: 1,
            playsinline: 1,
          },
          events: {
            onReady: function (e) {
              var offset = Math.min(Math.max(0, self.elapsed), self.durationSeconds);
              e.target.seekTo(offset, true);
              e.target.playVideo();
            },
          },
        });
        // Correct drift back to the server-derived position every 15s.
        self._driftHandle = setInterval(function () {
          if (!self.player || !self.player.getCurrentTime) return;
          var desired = Math.min(self.elapsed, self.durationSeconds);
          var actual = self.player.getCurrentTime();
          if (Math.abs(desired - actual) > 4 && desired < self.durationSeconds) {
            self.player.seekTo(desired, true);
          }
        }, 15000);
      }

      if (window.YT && window.YT.Player) {
        create();
        return;
      }
      // Load the IFrame API once.
      window.onYouTubeIframeAPIReady = create;
      if (!document.getElementById("yt-iframe-api")) {
        var s = document.createElement("script");
        s.id = "yt-iframe-api";
        s.src = "https://www.youtube.com/iframe_api";
        document.body.appendChild(s);
      }
    },

    // --- tips ticker ---
    startTicker() {
      var tips = window.CREDIT_TIPS || ["Educational information only."];
      var self = this;
      var i = Math.floor(Math.random() * tips.length);
      this.tip = tips[i];
      this.tipKey++;
      function rotate() {
        var n = Math.floor(Math.random() * tips.length);
        if (tips.length > 1 && n === i) n = (n + 1) % tips.length;
        i = n;
        self.tip = tips[i];
        self.tipKey++;
        self._tipHandle = setTimeout(rotate, 5000 + Math.random() * 4000);
      }
      this._tipHandle = setTimeout(rotate, 5000);
    },

    offerCourse() {
      if (window.TN) window.TN.track("course_cta", { from: "webinar" });
      window.location.href = "/coaching?focus=course&track=" + this.audience;
    },
    offerCoaching() {
      if (window.TN) window.TN.track("coaching_cta", { from: "webinar" });
      window.location.href = "/coaching?track=" + this.audience;
    },

    destroy() {
      clearInterval(this._tickHandle);
      clearInterval(this._resyncHandle);
      clearInterval(this._driftHandle);
      clearTimeout(this._tipHandle);
    },
  };
}
window.webinarRoom = webinarRoom;
