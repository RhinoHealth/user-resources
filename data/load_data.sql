-- load_data.sql

-- Function to load CSV files matching a pattern
CREATE OR REPLACE FUNCTION load_csv_files(pattern text, table_name text, columns text)
RETURNS void AS $$
DECLARE
    file_path text;
BEGIN
    FOR file_path IN
        SELECT pg_ls_dir('/extracted_data') AS filename
        WHERE pg_ls_dir('/extracted_data') LIKE pattern
    LOOP
        EXECUTE format('COPY %I(%s) FROM %L DELIMITER '','' CSV HEADER',
                      table_name,
                      columns,
                      '/extracted_data/' || file_path);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Load all matching files for each table
SELECT load_csv_files('%users%.csv', 'users', 'name, email');
SELECT load_csv_files('%products%.csv', 'products', 'name, price, stock');

-- Clean up the function
DROP FUNCTION load_csv_files;