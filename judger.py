import subprocess, resource, time, sys
import pprint

def make_command(lang, file_name, memory_limit): # in MB
    ret = "ulimit -s unlimited; "
    
    if lang == "java":
        ret += "javac {}.java; java -Xmx{}m Solution".format(file_name, memory_limit)
        return ret
    
    ret += "ulimit -v {}; ".format(memory_limit * 1024)
    
    if lang == "cpp":
        ret += "g++ ./{}.cpp -o {}; ./{}".format(file_name, file_name, file_name)
    elif lang == "py3":
        ret += "python3 {}.py".format(file_name)
    elif lang == "c":
        ret += "gcc ./{}.c -o {}; ./{}".format(file_name, file_name, file_name)
        
    return ret

"""
    *** Exit Code ***
    Accepted : 0
    Wrond Answer : 1
    Time Limit Exceed : 2
    Memory Limit Exceed : 3
    Compile / Runtime Error : 4
"""
def judge(prob_num, lang, file_name, time_limit, memory_limit, testcase_number):
    len_limit = 20
    
    ret = {
        "jury_stdout": "",
        "user_stdout": "",
        "stdin": "",
        "msg": "",
        "exit_code": 0,
        "time": 0, # In Seconds
        "memory": 0, # In KB
        "lang": lang,
        "details": ""
    }
    
    p = subprocess.Popen(make_command(lang, file_name, memory_limit), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdin = open("./{}/{}.in".format(prob_num, testcase_number), "r").read()
    
    temp = stdin.split("\n")
    for i in temp:
        if len(i) > len_limit:
            ret["stdin"] += i[:len_limit] + "..."
        else:
            ret["stdin"] += i
        ret["stdin"] += "\n"
    
    stdin = stdin.encode()
    
    try:
        start_time = time.time()
        stdout, stderr = p.communicate(input=stdin, timeout=time_limit)
        p.wait()
        end_time = time.time()
        
        ret["time"] = end_time - start_time
        ret["memory"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        
        stdout = stdout.decode("UTF-8").strip().strip("\n")
        ret["details"] = stderr.decode("UTF-8")
        
        return_code = p.poll()
        
        if return_code:
            if "Memory" in ret["details"]:
                ret["exit_code"] = 3
                ret["msg"] = "Memory Limit Exceed"
            else:
                ret["exit_code"] = 4
                ret["msg"] = "Compile / Runtime Error"
        else:
            out1 = stdout.split("\n")
            out2 = open("./{}/{}.out".format(prob_num, testcase_number), "r").read().strip().strip("\n").split("\n")
            
            flag = True
            for i in range(len(out2)):
                sb1 = out1[i].strip()
                sb2 = out2[i].strip()
                
                if len(sb1) > len_limit:
                    ret["user_stdout"] += sb1[:len_limit] + "..."
                else:
                    ret["user_stdout"] += sb1
                ret["user_stdout"] += "\n"
                
                if len(sb2) > len_limit:
                    ret["jury_stdout"] += sb2[:len_limit] + "..."
                else:
                    ret["jury_stdout"] += sb2
                ret["jury_stdout"] += "\n"
                
                if sb1 != sb2:
                    flag = False
                    ret["exit_code"] = 1
                    ret["msg"] = "Wrong Answer"
                    ret["details"] = "Wrong Answer in Line {}.".format(i + 1)
                    break
            
            if flag:
                ret["exit_code"] = 0
                ret["msg"] = "Accepted"
                ret["details"] = "Correct All {} Lines".format(len(out2))
    
    except subprocess.TimeoutExpired:
        ret["exit_code"] = 2
        ret["msg"] = "Time Limit Exceed"
    
    ret["time"] = int(ret["time"] * 1000)
    
    return ret
    
    
# 100000개 입력 기준 
# C++의 경우 1억이면 1초 
# C의 경우 1억이면 1초
# 자바의 경우 컴파일 시간 +1초
# 파이썬의 경우 1억에 10초 

# [Problem Number] [Language] [Filename] [Time Limit(s)] [Memory Limit(MB)] [The Number of Testcases]
# python3 judger.py 1 py3 solution 1 256 4
if __name__ == '__main__':
    args = sys.argv
    
    prob_num=int(args[1])
    lang=args[2]
    filename=args[3]
    timelimit=int(args[4])
    memorylimit=int(args[5])
    num_of_tc=int(args[6])
    
    ret = {
        "prob_num" : prob_num,
        "lang" : lang,
        "submit_id" : filename,
        "msg" : "Accepted",
        "details" : "All {} Testcases Passed.".format(num_of_tc),
        "exit_code" : 0,
        "execution_time" : 0,
        "memory_usage" : 0,
        "testcase_info" : []
    }
    
    for i in range(1,num_of_tc+1):
        judge_result = judge(prob_num, lang, filename, timelimit, memorylimit, i)
        
        ret["execution_time"]=max(ret["execution_time"],judge_result["time"])
        ret["memory_usage"]=max(ret["memory_usage"],judge_result["memory"])
        ret["testcase_info"].append({
            "testcase_number": i,
            "exit_code": judge_result["exit_code"],
            "execution_time": judge_result["time"],
            "memory_usage": judge_result["memory"],
            "stdin": judge_result["stdin"],
            "msg": judge_result["msg"],
            "details": judge_result["details"],
            "user_stdout": judge_result["user_stdout"],
            "jury_stdout": judge_result["jury_stdout"]
        })
        
        if judge_result["exit_code"] != 0:
            ret["msg"] = judge_result["msg"]
            ret["details"] = "{} in Testcase #{}.".format(ret["msg"], i)
            ret["execution_time"]=0
            ret["memory_usage"]=0
            break
        
    
    pprint.pprint(ret)