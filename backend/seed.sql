-- Tranzformation Nation -- seed data (SQLite-compatible).
-- The admin password hash below is a REAL bcrypt hash of the demo password
-- "password" so the admin logs in out of the box. Demo creds (see README):
--   admin@example.com / password
-- Rotate this immediately for any real deployment.

INSERT INTO users (email, password_hash, first_name, last_name, role, approval_status, email_verified, marketing_opt_in)
VALUES ('admin@example.com', '$2b$12$XzCiQy1o9PF0V/FWXOgJVOevj/TwAogvfyF9mo7W4qGprx/I3OUEy', 'Site', 'Admin', 'admin', 'approved', 1, 0);

-- Default webinar configuration (placeholder YouTube id; override via env WEBINAR_YOUTUBE_ID).
INSERT INTO webinar_config (audience, title, youtube_id, duration_seconds, interval_minutes, course_reveal_seconds, offer_reveal_seconds)
VALUES ('customer', 'Customer Credit Action Training (Pre-Recorded)', 'dQw4w9WgXcQ', 3120, 15, 1200, 2520);

INSERT INTO webinar_config (audience, title, youtube_id, duration_seconds, interval_minutes, course_reveal_seconds, offer_reveal_seconds)
VALUES ('agent', 'Credit Education Business Foundations (Pre-Recorded)', 'dQw4w9WgXcQ', 3600, 15, 1500, 3000);

-- Customer course modules + lessons.
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('customer', 'Understanding the System', 'How reports and scores work, and where the data comes from.', 1);
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('customer', 'Organizing Your Review', 'A calm, documented way to read your own report.', 2);
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('customer', 'Errors vs. Accurate Negatives', 'What you can dispute, and what generally cannot be removed.', 3);
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('customer', 'Building a Responsible Action Plan', 'Turn your review into clear, lawful next steps.', 4);

INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (1, 'Reports vs. Scores', 'A credit report is your file; a score is a number derived from it. They are not the same thing. Educational only.', 'dQw4w9WgXcQ', 8, 1);
INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (1, 'The Three Reporting Agencies', 'Equifax, Experian, and TransUnion may hold different data, which is why scores can differ.', 'dQw4w9WgXcQ', 7, 2);
INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (2, 'Reading Your Report Calmly', 'Personal info, accounts, payment history, collections, public records, and inquiries.', 'dQw4w9WgXcQ', 9, 1);
INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (3, 'When a Dispute Is Appropriate', 'Dispute only information you believe is inaccurate, incomplete, outdated, duplicated, or not yours.', 'dQw4w9WgXcQ', 10, 1);
INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (4, 'Your 30-Day Action Plan', 'Create a document folder, record correspondence, review utilization, protect payment history.', 'dQw4w9WgXcQ', 6, 1);

-- Agent course modules.
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('agent', 'The Business Model', 'Credit education vs. credit repair, and why guarantees are dangerous.', 1);
INSERT INTO modules (audience, title, summary, sort_order)
VALUES ('agent', 'Compliance Foundation', 'Disclosures, written agreements, cancellation rights, advertising standards.', 2);

INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (5, 'Education vs. Repair', 'Define what your business will and will not provide. Avoid guaranteed-result language.', 'dQw4w9WgXcQ', 9, 1);
INSERT INTO lessons (module_id, title, body, video_id, duration_minutes, sort_order)
VALUES (6, 'Required Disclosures', 'CROA and state CSO laws may require contracts, disclosures, and cancellation notices.', 'dQw4w9WgXcQ', 11, 1);
