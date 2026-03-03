### 说明现在老的提交方式 账号+密码已不能提交到github仓库了 所以改为ssh and GPG keys的方式提交到github仓库
操作如下 
1. 本地生成 SSH key： 
ssh-keygen -t ed25519 -C "lxyxd_2019@outlook.com" 

```

(base) xiaoyongliu@xiaoyongs-iMac /tmp % cd ~/.ssh/   
(base) xiaoyongliu@xiaoyongs-iMac .ssh % ls -la
total 32
drwx------   6 xiaoyongliu  staff   192 Mar  3 15:55 .
drwxr-x---+ 64 xiaoyongliu  staff  2048 Mar  3 15:54 ..
-rw-------   1 xiaoyongliu  staff   419 Mar  3 15:55 id_ed25519       
-rw-r--r--   1 xiaoyongliu  staff   104 Mar  3 15:55 id_ed25519.pub --->这个就是pub key文件
-rw-------   1 xiaoyongliu  staff  1845 Feb 25 11:40 known_hosts
-rw-------   1 xiaoyongliu  staff  1111 Feb 25 11:40 known_hosts.old
```

2. 把公钥添加到 GitHub → Settings → SSH and GPG keys → Add new SSH Key

```
SSH keys
This is a list of SSH keys associated with your account. Remove any keys that you do not recognize.

Authentication keys
SSH
lxyxd_2019@outlook.com
SHA256:rWUHDjlacuNbROSZaL6/lTIyov99ZXMF4D3VZhIF/oM
Added on Mar 3, 2026
Last used within the last week — Read/write
Check out our guide to connecting to GitHub using SSH keys or troubleshoot common SSH problems.

```
3. 把仓库的远程地址改成 SSH：
git remote set-url origin git@github.com:liuxiaoyong2022/langchain-ai-agent.git

```
(base) xiaoyongliu@xiaoyongs-iMac langchain-ai-agent % git remote set-url origin git@github.com:liuxiaoyong2022/langchain-ai-agent.git
(base) xiaoyongliu@xiaoyongs-iMac langchain-ai-agent % git push -u origin main                                                        
The authenticity of host 'github.com (20.205.243.166)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'github.com' (ED25519) to the list of known hosts.
Enumerating objects: 510, done.
Counting objects: 100% (510/510), done.
Delta compression using up to 4 threads
Compressing objects: 100% (500/500), done.
Writing objects: 100% (510/510), 4.95 MiB | 1.79 MiB/s, done.
Total 510 (delta 33), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (33/33), done.
To github.com:liuxiaoyong2022/langchain-ai-agent.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```
