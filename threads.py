import os
import time
from threading import Thread, Lock

results = {}
lock = Lock()


def search_keywords_in_files(files, keywords):
    local_results = {word: [] for word in keywords}
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                for word in keywords:
                    if word.lower() in content.lower():
                        local_results[word].append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    with lock:
        for word, found_files in local_results.items():
            results[word].extend(found_files)


def multithreaded_search(file_list, keywords, num_threads=4):
    threads = []
    chunk_size = max(1, len(file_list) // num_threads)

    for i in range(num_threads):
        chunk = file_list[i * chunk_size:(i + 1) * chunk_size]
        thread = Thread(target=search_keywords_in_files, args=(chunk, keywords))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_all_files(dir_path, file_extension=".txt"):
    return [os.path.join(root, file)
            for root, _, files in os.walk(dir_path)
            for file in files if file.endswith(file_extension)]


if __name__ == "__main__":
    directory = "texts/Закони"
    keywords = ["закон", "право", "кодекс"]

    file_list = get_all_files(directory)
    if not file_list:
        print("No text files found.")
    else:
        print(f"Processing {len(file_list)} files...")

        results = {word: [] for word in keywords}
        start_time = time.time()
        multithreaded_search(file_list, keywords)
        end_time = time.time()

        for word, files in results.items():
            print(f'"{word}" found in: {files}')
        print(f"Time: {end_time - start_time:.2f}s")