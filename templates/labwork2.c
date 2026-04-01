#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>
int main() {
 pid_t pid = fork();
 if(pid == 0) {
 printf("Child process executing\n");
 exit(0);
 } else {
 wait(NULL);
 printf("Parent process resumes after child finishes\n");
 }
 return 0;
}