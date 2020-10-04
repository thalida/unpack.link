import glob
import profile
import pstats

profile_files = glob.glob('/tmp/unpack_profiler_*_results.txt')
stats = pstats.Stats(profile_files[0])
for pr_file in profile_files:
    if pr_file == profile_files[0]:
        continue
    stats.add(pr_file)

stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats()

print(profile_files[0])
