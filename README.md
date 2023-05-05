# CS-5363-001-Spring-2023-Programming Lang & Compilers
# Project Phase III: Semantic Analizer and Code Generation
# By Eulises Franco

Python Semantic Analizer and Code Generation for DECAF22

Project Phase III consists in building a Semantic Analizer for the "Decaf 22" programming language

In order to run this program go inside workdir directory.
Make sure exec.sh has executable permissions.

If script has executable permissions:
    use command ./exec.sh <file path>   to execute.
    If errors are encountered in the semantic analizer phase, such errors will be displayed on screen
    If no errors encountered. A t1.s file will be generated and saved in workdir directory.
    Then SPIM will be ran from the terminal executing the t1.s file to run the code generated.
    
To add executable permissions in linux use command:
    chmod +x filename
    when in workdir directory:
        do chmod +x exec.sh
        then 
        do chmod +x ../pp3-post/spim/spim
         


!!!! Important !!!!
Make sure main.py and utils.py are on the same directory outside workdir.
When running the command must be executed inside workdir and main.py and utils.py must be outside of workdir directory.