from scp import SCPClient
import paramiko
import os
from pathlib import Path,PurePath
import config as config

def connect_host_SSH(server:str,username:str,password:str)->paramiko.client.SSHClient:
    client=paramiko.client.SSHClient()
    client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    client.connect(server, username=username, password=password)
    return client

def connect_host_SFTP(server:str,username:str,password:str)->paramiko.Transport:
    client=paramiko.Transport(server)
    client.connect(username=username, password=password)
    return client

def mkdir_remote(sftp:paramiko.SFTPClient,remotepath:str)->None:
    try:
        sftp.chdir(remotepath)
    except:
        sftp.mkdir(remotepath)
        print("MAKEDIR", remotepath)
    else:
        print("SKIPMAKEDIR", remotepath)
        return None

def copy_files(sftp:paramiko.SFTPClient,from_dir:str,target_dir:str):
    filesArray=list(iter(Path(from_dir).glob("*")))
    if(len(filesArray)==0):
        return
    else:
        for file in filesArray:
            target_file_loc = target_dir +"/"+ PurePath(file).stem
            if(file.is_dir()):
                mkdir_remote(sftp,str(PurePath(target_file_loc).parent))
                copy_files(sftp,str(file),target_file_loc)
            else:
                mkdir_remote(sftp, str(PurePath(target_file_loc).parent))
                try:
                    sftp.put(str(file),target_file_loc)
                    print("COPY",file,target_file_loc)
                except:
                    print("SKIP",file, target_file_loc)
                    continue




def main():
    transport=connect_host_SFTP(config.server,config.username,config.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    copy_files(sftp,config.FROM_PATH,config.TO_PATH)

    transport.close()


if __name__ == '__main__':
    main()