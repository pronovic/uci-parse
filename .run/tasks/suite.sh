# vim: set ft=bash sw=3 ts=3 expandtab:
# runscript: customized=true

help_suite() {
   echo "- run suite: Run the complete test suite, as for the GitHub Actions CI build"
   echo "- run suite -f: Run a faster version of the test suite, ommitting some steps"
}

task_suite() {
   if [ "$1" == "-f" ]; then
      run_command pythonversion
      run_task install
      run_task checks
      run_task test
   else
      run_command pythonversion
      run_task install
      run_task checks
      run_task build
      run_task test -c
      run_task docs
      run_command pythonversion
   fi
}
