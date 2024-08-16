from human_eval.data import read_problems, write_jsonl, stream_jsonl
import glob 
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()

# Inputs
parser.add_argument(
    '--path',
    type=str,
    help="")
parser.add_argument(
    '--out_path',
    type=str,
    help="")
parser.add_argument(
    '--add_prompt',
    action='store_true',
    help='')

args = parser.parse_args()


files = sorted(glob.glob(args.path + '/*.jsonl'))
print("{} files in {}".format(len(files), args.path))

problems = read_problems()

output = []
a = 0
for code_file in tqdm(files, total=len(files)):
    codes = [c for c in stream_jsonl(code_file)]
    if args.add_prompt: 
        for code in codes: 
            task_id = code['task_id']
            prompt = problems[task_id]['prompt']
            completion = code['completion']
            completion = completion.replace("\r", "")            
            if '```python' in completion: 
                def_line = completion.index('```python')
                completion = completion[def_line:].strip()
                completion = completion.replace('```python', '')
                # print(completion)
                try:
                    next_line = completion.index('```')
                    completion = completion[:next_line].strip()
                except:
                    a += 1
                    print(completion)
                    print("================\n")
                # print(completion)
            if "__name__ == \"__main__\"" in completion:
                next_line = completion.index('__name__ == "__main__"')
                completion = completion[:next_line].strip()
                # print(completion)
            
            if "# Example usage" in completion:
                # print(completion)
                next_line = completion.index('# Example usage')
                completion = completion[:next_line].strip()
            
            code['completion'] = completion
    
    output += codes 
    
print("save to {}".format(args.out_path))
write_jsonl(args.out_path, output)
print(a)
