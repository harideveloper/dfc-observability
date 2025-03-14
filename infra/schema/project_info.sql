CREATE TABLE `dev2-ea8f.observability.project_info`
(
    project_id STRING NOT NULL OPTIONS(description="Project ID"),
    project_number STRING NOT NULL OPTIONS(description="Project Number"),
    folder_id STRING OPTIONS(description="Folder ID"),
    project_name STRING OPTIONS(description="Project display name"),
    state STRING OPTIONS(description="Project status"),
    create_time TIMESTAMP OPTIONS(description="Project creation timestamp"),
    update_time TIMESTAMP OPTIONS(description="Project last updated timestamp"),
    ingestion_time TIMESTAMP OPTIONS(description="Ingestion timestamp"),
    etag STRING OPTIONS(description="IAM Roles"),
    labels ARRAY<STRUCT<
        key STRING,
        value STRING
    >> OPTIONS(description="Custom labels")
)
PARTITION BY DATE(ingestion_time)  
CLUSTER BY project_id, state, folder_id 
OPTIONS(
    description="dfc project information with ingestion time partitioning",
    expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
);
