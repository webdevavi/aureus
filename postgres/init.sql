CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE file_category AS ENUM ('source', 'extract', 'output');
CREATE TYPE file_type AS ENUM ('pdf', 'json', 'txt');
CREATE TYPE file_status AS ENUM ('pending', 'processing', 'done', 'error');

CREATE TABLE IF NOT EXISTS report_files (
    id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(id) ON DELETE CASCADE,
    type file_type NOT NULL,
    category file_category NOT NULL,
    s3_bucket TEXT DEFAULT 'reports',
    s3_key TEXT NOT NULL,
    status file_status DEFAULT 'pending',
    error TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),


    CONSTRAINT uix_report_category UNIQUE (report_id, category),
    CONSTRAINT uix_report_s3key UNIQUE (report_id, s3_key)
);

CREATE INDEX IF NOT EXISTS idx_report_files_report_id ON report_files(report_id);