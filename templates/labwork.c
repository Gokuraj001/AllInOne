#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

int main() {
 pid_t pid;
 pid = fork();
 if(pid == 0) {
 printf("Child Process\n");
 printf("Child PID: %d\n", getpid());
 } else {
 printf("Parent Process\n");
 printf("Parent PID: %d\n", getpid());
 }
 return 0;
}