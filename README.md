# borg_exporter
A prometheus exporter/node_exporter text collector for borg backup



## Usage
    usage: borg_exporer.py [-h] -c CONFIG -o OUTPUT

    pihole_exporter

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            borg_exporter config
      -o OUTPUT, --output OUTPUT
                            text collector dir

## Example Metrics

    borg_repo_archives_count{repo="/path/to/repo"} 3
    borg_repo_total_size{repo="/path/to/repo"} 396595027.000000
    borg_repo_unique_size{repo="/path/to/repo"} 93921486.000000
    borg_repo_total_csize{repo="/path/to/repo"} 396966676.000000
    borg_repo_total_unique_chunks{repo="/path/to/repo"} 2829.000000
    borg_repo_total_chunks{repo="/path/to/repo"} 8643.000000
    borg_repo_unique_csize{repo="/path/to/repo"} 94043133.000000
    borg_archive_duration{client_hostname="testhost", name="testhost-2019-03-01T14:22:43.877660", repo="/path/to/repo"} 34.564274
    borg_archive_original_size{client_hostname="testhost", name="testhost-2019-03-01T14:22:43.877660", repo="/path/to/repo"} 131474383.000000
    borg_archive_nfiles{client_hostname="testhost", name="testhost-2019-03-01T14:22:43.877660", repo="/path/to/repo"} 2849.000000
    borg_archive_deduplicated_size{client_hostname="testhost", name="testhost-2019-03-01T14:22:43.877660", repo="/path/to/repo"} 313693.000000
    borg_archive_compressed_size{client_hostname="testhost", name="testhost-2019-03-01T14:22:43.877660", repo="/path/to/repo"} 131597879.000000
    borg_archive_duration{client_hostname="testhost", name="testhost-2019-03-01T15:53:32.732150", repo="/path/to/repo"} 4.160368
    borg_archive_original_size{client_hostname="testhost", name="testhost-2019-03-01T15:53:32.732150", repo="/path/to/repo"} 131474383.000000
    borg_archive_nfiles{client_hostname="testhost", name="testhost-2019-03-01T15:53:32.732150", repo="/path/to/repo"} 2849.000000
    borg_archive_deduplicated_size{client_hostname="testhost", name="testhost-2019-03-01T15:53:32.732150", repo="/path/to/repo"} 72288.000000
    borg_archive_compressed_size{client_hostname="testhost", name="testhost-2019-03-01T15:53:32.732150", repo="/path/to/repo"} 131597879.000000
    borg_archive_duration{client_hostname="testhost", name="testhost-2019-03-01T22:00:19.263098", repo="/path/to/repo"} 6.472217
    borg_archive_original_size{client_hostname="testhost", name="testhost-2019-03-01T22:00:19.263098", repo="/path/to/repo"} 131474396.000000
    borg_archive_nfiles{client_hostname="testhost", name="testhost-2019-03-01T22:00:19.263098", repo="/path/to/repo"} 2849.000000
    borg_archive_deduplicated_size{client_hostname="testhost", name="testhost-2019-03-01T22:00:19.263098", repo="/path/to/repo"} 139533.000000
    borg_archive_compressed_size{client_hostname="testhost", name="testhost-2019-03-01T22:00:19.263098", repo="/path/to/repo"} 131597892.000000
