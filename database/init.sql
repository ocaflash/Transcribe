CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    drive_file_id VARCHAR(255) NOT NULL,
    drive_file_link VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    tag VARCHAR(255)
);

CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    text TEXT NOT NULL,
    language VARCHAR(50),
    translated_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Функция для обновления поля updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления поля updated_at
CREATE TRIGGER trigger_update_updated_at
BEFORE UPDATE ON transcriptions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_transcriptions_file_id ON transcriptions(file_id);
