#!/usr/bin/env python3
"""
CMS.gov API Configuration

Configuration settings for downloading data from CMS.gov Provider Data API
"""

# CMS.gov API Configuration
CMS_CONFIG = {
    'base_url': 'https://data.cms.gov/provider-data/api/1/datastore',
    'output_dir': 'cms_data',
    'dataset_id': 'a678955c-467c-5df1-a8bf-c94d22c86247',  # Your dataset ID
    'default_params': {
        'show_db_columns': ''
    }
}

# Common SQL queries for different data needs
QUERIES = {
    'sample_10': '[SELECT * FROM {dataset_id}][LIMIT 10]',
    'sample_100': '[SELECT * FROM {dataset_id}][LIMIT 100]',
    'sample_1000': '[SELECT * FROM {dataset_id}][LIMIT 1000]',
    'all_data': '[SELECT * FROM {dataset_id}]',
    'count_records': '[SELECT COUNT(*) FROM {dataset_id}]',
    'schema_info': '[SELECT * FROM {dataset_id}][LIMIT 1]'  # To understand data structure
}

# File naming conventions
FILE_NAMES = {
    'sample_10': 'cms_sample_10_records.json',
    'sample_100': 'cms_sample_100_records.json',
    'sample_1000': 'cms_sample_1000_records.json',
    'all_data': 'cms_full_dataset.json',
    'count_records': 'cms_record_count.json',
    'schema_info': 'cms_data_schema.json'
}

def get_query_params(query_type: str, dataset_id: str = None) -> dict:
    """
    Generate query parameters for CMS API
    
    Args:
        query_type: Type of query from QUERIES dict
        dataset_id: Dataset ID (uses default if not provided)
        
    Returns:
        dict: Query parameters for API call
    """
    if dataset_id is None:
        dataset_id = CMS_CONFIG['dataset_id']
        
    if query_type not in QUERIES:
        raise ValueError(f"Unknown query type: {query_type}. Available: {list(QUERIES.keys())}")
    
    query = QUERIES[query_type].format(dataset_id=dataset_id)
    
    return {
        'query': query,
        **CMS_CONFIG['default_params']
    }

def get_filename(query_type: str) -> str:
    """Get standardized filename for query type"""
    return FILE_NAMES.get(query_type, f'cms_{query_type}.json')
