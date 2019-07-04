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

# import glob
# import cProfile
# import pstats

# def quick():
#     pass

# combined_filename = '/tmp/unpack_profiler_results_all.txt'
# print(cProfile)
# # pr = cProfile.Profile()
# pr.run('quick()', combined_filename)
# stats = pstats.Stats(combined_filename)

# profile_files = glob.glob('/tmp/unpack_profiler_*_results.txt')
# for pr_file in profile_files:
#     stats.add(pr_file)

# stats.strip_dirs()
# stats.sort_stats('cumulative')
# stats.print_stats()

# print(combined_filename)
