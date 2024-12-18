import os
import time
from multiprocessing import Process, Queue


def search_keywords_in_files(files, keywords, queue):
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

    queue.put(local_results)


def multiprocessed_search(file_list, keywords, num_processes=4):
    processes = []
    queue = Queue()
    chunk_size = max(1, len(file_list) // num_processes)

    for i in range(num_processes):
        chunk = file_list[i * chunk_size:(i + 1) * chunk_size]
        proc = Process(target=search_keywords_in_files, args=(chunk, keywords, queue))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    results = {word: [] for word in keywords}
    while not queue.empty():
        local_results = queue.get()
        for word, found_files in local_results.items():
            results[word].extend(found_files)

    return results


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

        start_time = time.time()
        results = multiprocessed_search(file_list, keywords)
        end_time = time.time()

        for word, files in results.items():
            print(f'"{word}" found in: {files}')
        print(f"Time: {end_time - start_time:.2f}s")