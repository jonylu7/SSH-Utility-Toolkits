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
        sftp.mkdir(remotepath)
        print("MAKEDIR", remotepath)
    except:
        print("SKIPMAKEDIR", remotepath)
        return None


def copy_files(sftp:paramiko.SFTPClient,from_dir:str,target_dir:str,TOTAL_FILES):
    nowcopy=0
    fromFilesArray=list(iter(Path(from_dir).glob("*")))
    toFilesArray=list(sftp.listdir(target_dir))

    if(len(fromFilesArray)==0):
        return
    else:
        for file in fromFilesArray:
            target_file_loc = target_dir +"/"+ PurePath(file).name
            if(file.is_dir()):
                mkdir_remote(sftp,str(PurePath(target_file_loc)))
                nowcopy+=copy_files(sftp,str(file),target_file_loc,TOTAL_FILES)
            else:
                try:
                    if(PurePath(file).stem in toFilesArray or PurePath(file).stem[0]=='.'):
                        print("SKIP", file, target_file_loc)
                        nowcopy += 1
                    else:
                        mkdir_remote(sftp, str(PurePath(target_file_loc).parent))
                        sftp.put(str(file), target_file_loc)
                        nowcopy += 1
                        print("COPY", file, target_file_loc)
                    print("Progress:{}/{}".format(nowcopy, TOTAL_FILES))
                except:
                    print("FAILED",file, target_file_loc)
    return nowcopy



def calculateTotalFiles(from_dir:str)->int:
    count=0
    filesArray = list(iter(Path(from_dir).glob("*")))
    for file in filesArray:
        if (file.is_dir()):
            count+=calculateTotalFiles(str(file))
        else:
            count+=1
    return count



def main():
    transport=connect_host_SFTP(config.server,config.username,config.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    TOTAL_FILES=calculateTotalFiles(config.FROM_PATH)
    copy_files(sftp,config.FROM_PATH,config.TO_PATH,TOTAL_FILES)

    transport.close()
    sftp.close()


if __name__ == '__main__':
    main()