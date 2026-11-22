# HTTP Data Fetching Memory Optimization

This example demonstrates memory-efficient HTTP data fetching, crucial for environments with limited RAM. It uses Python's `requests` library with streaming (`iter_lines`) and generators to process data from multiple mock financial endpoints without loading entire responses or all parsed objects into memory simultaneously.

## Language

`python`

## How to Run

1. Install requests: `pip install requests`
2. Run the script: `python main.py`

## Original Article

This example accompanies the Turkish article: [4.400+ Finans Uygulamasından HTTP ile Veri Çekimi: RAM Optimizasyonu ve Dersler](https://fatihsoysal.com/blog/4-400-finans-uygulamasindan-http-ile-veri-cekimi-ram-optimizasyonu-ve-dersler/).

## License

MIT — see [LICENSE](LICENSE).
