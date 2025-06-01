
class PluginIoC:
    def __init__(self):
        pass

    def build_ioc(self, scdg, mem_bp_evasion, exp_dir):
        funcs = {
                "strings": ["lstrlenA","lstrlenW","strlen","lstrcpyA","lstrcpyW","strncpy","lstrcatA","lstrcatW","lstrcmpA","lstrcmpW","strcmp","strncmp"],
                "format": ["wsprintfA","wsprintfW","MultiByteToWideChar","WideCharToMultiByte"],
                "regs" :
                    ["RegCreateKeyExA","RegCreateKeyExW","RegCreateKeyA","RegCreateKeyW","RegSetValueExA","RegSetValueExW","RegSetValueA","RegSetValueW","RegQueryValueExW","RegQueryValueExA","RegQueryValueA","RegQueryValueW","RegOpenKeyA","RegOpenKeyW","RegOpenKeyExA","RegOpenKeyExW","RegDeleteKeyW","RegDeleteKeyA","RegGetValueA","RegGetValueW",],
                "files" :
                    ["CreateFileA","CreateFileW","GetModuleFileNameA","GetModuleFileNameW","GetTempPathA","GetTempPathW","FindFirstFileW","FindFirstFileA","WriteFile","ReadFile","CopyFile"],
                "dir" :
                    ["CreateDirectoryA","CreateDirectoryW","SHGetFolderPathW","SHGetFolderPathA","GetWindowsDirectoryW","GetWindowsDirectoryA","SHGetSpecialFolderPathW","SHGetSpecialFolderPathA"],
                "network" :
                    ["getaddrinfo","gethostbyname","inet_addr","NetLocalGroupAddMembers","socket","bind","listen","accept","connect","recv","shutdown","WSAStratup","WSACleanup","send"],
                "cmd" :
                    ["ShellExecuteW","ShellExecuteA","ShellExecuteExW","ShellExecuteExA","WinExec"],
                "thread" :
                    ["ResumeThread","NtResumeThread","CreateThread","GetThreadContext","SetThreadContext"],
                "process" :
                    ["CreateProcessA","CreateProcessW","ReadProcessMemory","NtWriteVirtualMemory","CreateRemoteThread","NtUnmapViewOfSection","WriteProcessMemory","VirtualAllocEx","ZwUnmapViewOfSection"],
                "other" : ["CreateEventA","CreateEventW","FindResourceW","FindResourceA","LookupAccountSidW","LookupAccountSidA","ExpandEnvironmentStringsW","GetDriveTypeW","GetDriveTypeA","URLDownloadToFileW","URLDownloadToFileA","GetLogicalDriveStringsW","GetLogicalDriveStringsA"],
                "lib" :
                    ["LoadLibraryA","LoadLibraryW","GetModuleHandleA","GetModuleHandleW"],
                "proc" :
                    ["GetProcAddress"],
                "services" :
                    ["OpenSCManager","CreateService","StartServiceCtrlDispatcher"],
                "crypt" :
                    ["CryptAcquireContext","CryptGenKey","CryptDeriveKey","CryptDecrypt","CryptReleaseContext"],
                "anti" :
                    ["IsDebuggerPresent","GetSystemInfo","GlobalMemoryStatusEx","GetVersion","CreateToolhelp32Snapshot"],
                "anti-debug" :
                    ["IsDebuggerPresent",
                        "CheckRemoteDebuggerPresent",
                        "NtQueryInformationProcess", # 0x1f, 0x1e, 0x7
                        "NtQueryProcessHeapInformation",
                        "NtQueryProcessDebugInformation",
                        "NtQuerySystemInformation", # 0x23 , ?ObjectTypeInformation?
                        "NtQueryObject",
                        "NtSystemDebugControl",
                        "CsrGetProcessId",
                        "WudfIsAnyDebuggerPresent",
                        "WudfIsKernelDebuggerPresent",
                        "WudfIsUserDebuggerPresent",
                        "NtSetInformationThread",],
        }

        # List of syscalls used to compare data in common IoC
        comparisons = ["_wcsicmp", "StrCmpW", "StrCmpNIW", "StrCmpIW", "StrCmpNI", "StrStrIW"]

        # IoC artifacts requiring one step analysis (find argument in syscall)
        # Keys are categories, each value is a list of syscall to look for
        one_step_ioc = {
            "common_loaded_dlls": ["GetModuleHandleW", "GetModuleHandleA"],
            "common_files": ["GetFileAttributesW", "GetFileAttributesA"],
            "common_devices": ["CreateFileW", "CreateFileA"]
        }

        # IoC artifacts requiring two step analysis (find argument in syscall, then find a
        # comparison function using the argument)
        # Keys are categories, each value is a list of (syscall, interesting_id) pair
        #     - 'interesting_id' is meant to be used with the function 'get_interesting_data'
        two_step_ioc = {
            "common_binary_name": [("PathFindFileNameW", -1), ("PathFindFileNameA", -1)],
            "common_user_names": [("GetUserNameW", 0), ("GetUserNameA", 0)],
            "common_computer_names": [("GetComputerNameW", 0), ("GetComputerNameA", 0), ("GetComputerNameExW", 1)],
            "common_processes": [("Process32FirstW", 1), ("Process32FirstA", 1), ("Process32NextW", 1), ("Process32NextA", 1)],
            "common_hw_properties": [("SetupDiGetDeviceRegistryPropertyW", 4), ("SetupDiGetDeviceRegistryPropertyA", 4)],
            "common_network_shared": [("WNetGetProviderNameW", 1), ("WNetGetProviderNameA", 1)]
        }


        # Special case: Extracting IoC out of regkey-related syscalls
        #   RegKeyOpen - list of syscall used to open a regkey (3-uple)
        #              - first is the name of the syscall
        #              - second is the interesting arg used to track the next syscall in call chain sequence
        #              - third is the regkey path to keep track of
        #
        #  RegKeyQuery - list of syscall used to query a regkey value (4-uple)
        #              - first is the name of the syscall
        #              - second is the interesting arg used to find the syscall in call chain sequence
        #              - third is the interesting arg used to track the next syscall in the call chain sequence
        #              - fourth is the regkey path to keep track of
        regkey_ioc = {
            "reg_key_open": [("RegOpenKeyExW", 4, 1)],
            "reg_key_query": [("RegQueryValueExW", 0, 4, 1)],
        }

        def get_interesting_data(call, index):
            """
            Get the return value of the syscall if the index is -1,
            Otherwise, get the value at the correct index in the syscall arguments
            """
            assert index >= -1
            assert index <= len(call["args"] if call["args"] is not None else [])
            return call["ret"] if index == -1 else call["args"][index]

        with open(exp_dir + "IoC_report.txt", 'w') as f:
            for func in funcs:
                strings = {""}
                f.write("\n #################################################################################### \n")
                f.write(func + "\n")
                for i in scdg:
                    for call in i:
                        if call["name"] in funcs[func]:
                            string = call["name"] + " ( "
                            for arg in call["args"]:
                                string += "<" + arg.__class__.__name__ + ">" + "[" + (str(arg) if type(arg) is not int else hex(arg)) + "], "
                                # if isinstance(arg,str): #and arg[-2:] != "32" and "_" not in arg and arg != "":
                                #    string = string + " " + arg + ","
                            if len(call["args"]) >= 1:
                                string = string[:-1]
                            string = "\t- " + string + "\x08" + " )\n"
                            if string not in strings:
                                f.write(string)
                                strings.add(string)



            #============================================#
            # Look for common artifacts IoC with one step#
            #============================================#
            for category_name, func_list in one_step_ioc.items():
                f.write(f"[+] ============= {category_name} ===============\n")
                
                # Holds the result of the analysis to pretty-print later
                one_step_results = dict()

                # Filter calls in one array
                one_step_syscalls = [call for i in scdg for call in i if call["name"] in func_list]
                for os_syscall in one_step_syscalls:
                    # Don't forget to populate the dict to avoid KeyError's
                    if os_syscall["name"] not in one_step_results.keys():
                        one_step_results[os_syscall["name"]] = []

                    # Construct the string with the IoC
                    target = ", ".join([str(os_syscall["args"][0])] if os_syscall["args"] is not None else [])
                    one_step_string = f"Checking the presence of [{target}]"

                    # Add the string with the IoC in the dict
                    if one_step_string not in one_step_results[os_syscall["name"]]:
                        one_step_results[os_syscall["name"]].append(one_step_string)

                # Pretty print the result in the IoC file
                for one_step_syscall, one_step_comps in one_step_results.items():
                    f.write(f"[+] ---- {one_step_syscall} ----\n")
                    [f.write("[+]" + comp + "\n") for comp in one_step_comps]

          
            #=============================================#
            # Look for common artifacts IoC with two steps#
            #=============================================#
            for category_name, func_list in two_step_ioc.items():
                f.write(f"[+] ============= {category_name} ===============\n")

                # Holds the syscall & interesting_id pairs in a dict
                pairs = dict(func_list)

                # Holds the results of the analysis to pretty-print later
                two_steps_results = dict()

                # Filter calls in one array
                two_steps_syscalls = [call for i in scdg for call in i if call["name"] in pairs.keys()]
                for ts_syscall in two_steps_syscalls:
                    if ts_syscall["name"] not in two_steps_results.keys():
                        two_steps_results[ts_syscall["name"]] = []

                    # Retrieve the id of the interesting argument, then the interesting argument
                    interesting_id = pairs[ts_syscall["name"]]
                    interesting_value = get_interesting_data(ts_syscall, interesting_id)
                    if not interesting_value:
                        continue

                    # Retrieve syscalls that appear in the comparisons list and which have the
                    # interesting argument in their own arguments/retval
                    two_steps_comparisons = [call for i in scdg for call in i if call["name"] in comparisons and interesting_value in call["args"]]

                    for ts_comp in two_steps_comparisons:
                        # Gather the arguments that are not already the interesting data
                        interesting_args = [str(arg) for arg in ts_comp["args"] if arg != interesting_value] if ts_comp["args"] is not None else []        

                        # Constructs the IoC string
                        target = " | ".join(interesting_args)
                        ts_string = f"'{interesting_value}' compared to '{target}'"

                        # Add the string with the IoC in the dict
                        if ts_string not in two_steps_results[ts_syscall["name"]]:
                            two_steps_results[ts_syscall["name"]].append(ts_string)
            
                # Pretty-print the result in the IoC file
                for two_steps_syscall, two_steps_comps in two_steps_results.items():
                    f.write(f"[+] ---- {two_steps_syscall} ----\n")
                    [f.write("[+]" + comp + "\n") for comp in two_steps_comps]

            #===================================#
            # Print IoC for registry keys checks#
            #===================================#
            f.write("[+] ============= common_reg_keys ===============\n")

            # Store the names of every syscall for ease of use
            rko_syscall_name_list = list(map(lambda rko: rko[0], regkey_ioc["reg_key_open"]))
            rkq_syscall_name_list = list(map(lambda rkq: rkq[0], regkey_ioc["reg_key_query"]))

            # Holds the results of the analysis to pretty-print later
            regkeys_results = dict()

            # Filter calls in one array
            regkey_open_syscalls = [call for i in scdg for call in i if call["name"] in rko_syscall_name_list]
            for rko_syscall in regkey_open_syscalls:
                # Get the interesting ids for the current syscall in one array for ease of use
                rko_interesting_ids = regkey_ioc["reg_key_open"][rko_syscall_name_list.index(rko_syscall["name"])]

                # Get the interesting data
                open_chain_id = get_interesting_data(rko_syscall, rko_interesting_ids[1])
                open_path = get_interesting_data(rko_syscall, rko_interesting_ids[2])

                # Retrieve the next syscalls in the call chain sequence
                regkey_query_syscalls = [call for i in scdg for call in i if call["name"] in rkq_syscall_name_list]
                for rkq_syscall in regkey_query_syscalls:

                    # Get the interesting ids for the current syscall in one array for ease of use
                    rkq_interesting_ids = regkey_ioc["reg_key_query"][rkq_syscall_name_list.index(rkq_syscall["name"])]

                    # Get the interesting values and skip uninteresting syscalls
                    query_chain_id =  get_interesting_data(rkq_syscall, rkq_interesting_ids[1])
                    if hex(open_chain_id) not in query_chain_id:
                        continue

                    query_value = get_interesting_data(rkq_syscall, rkq_interesting_ids[3])
                    if query_value in ("Count",):
                        continue

                    query_comparison = get_interesting_data(rkq_syscall, rkq_interesting_ids[2])

                    # Create a single name to represent the use of both open and query calls
                    open_query_name = rko_syscall["name"] + '-' + rkq_syscall["name"]
                    if open_query_name not in regkeys_results.keys():
                        regkeys_results[open_query_name] = []

                    # Retrieve the next syscalls in the call chain sequence
                    regkey_comparisons = [call for i in scdg for call in i if call["name"] in comparisons and query_comparison in call["args"]]
                    for rkc_syscall in regkey_comparisons:
                        # Retrieve the interesting args
                        rkc_interesting_args = [str(arg) for arg in rkc_syscall["args"] if arg != query_comparison] if rkc_syscall["args"] is not None else []        
                        # Construct the IoC string
                        target = " | ".join(rkc_interesting_args)
                        rkc_string = f"Searched '{target}' in [{open_path}]:[{query_value}]"
                        # Add the string with the IoC in the result dict
                        if rkc_string not in regkeys_results[open_query_name]:
                            regkeys_results[open_query_name].append(rkc_string)

            # Pretty-print the results in the IoC file
            for regkey_syscalls, regkey_comps in regkeys_results.items():
                f.write(f"[+] ---- {regkey_syscalls} ----\n")
                [f.write("[+]" + comp + "\n") for comp in regkey_comps]

            #========================================#
            # Print IoC for memory access breakpoints#
            #========================================#
            f.write("[+] ============= mem_access_breakpoints ===============\n")
            # Print the result of the memory breakpoint analysis
            for mem_bp_class, mem_bp_addr, mem_bp_offset in set(mem_bp_evasion):
                mem_bp_string = f"[+]\t- Access to structure '{mem_bp_class}' at offset '{mem_bp_offset}' detected (addr={mem_bp_addr})\n"
                f.write(mem_bp_string)
