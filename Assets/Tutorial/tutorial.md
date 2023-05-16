# Table of Contents
- [Introduction](#merivale-io)
    - [Premise](#premise)
    - [Completing Tasks](#completing-tasks)
- [Microcoded Hardware System](#microcoded-hardware-system)
    - [Registers](#registers)
    - [General Commands](#general-commands)
        - [mov](#mov)
        - [jmp](#jmp)
        - [slp](#slp)
    - [Arithmetic Commands](#arithmetic-commands)
        - [add](#add)
        - [sub](#sub)
        - [mul](#mul)
    - [Logical Commands](#logical-commands)
        - [tis](#tis)
        - [tgt](#tgt)
        - [tlt](#tlt)
        - [not](#not)
    - [Example Program](#example-program)


# Merivale I/O
Welcome to Merivale I/O! This document will prepare you for designing solutions to various tasks and puzzles!

## Premise
In Merivale I/O, you design circuits. Each level, you are given a task to complete, and need to come up with a solution using the available Microcontrollers and Wires.  
To place wires, click with your mouse on a grid square, and to remove wires, right click.  
To place a microcontroller, click the `E` key while hovering over a grid square with your mouse. To remove a microcontroller, press `Q` while hovering over one.  
  
## Completing Tasks
Given a task, you will place microcontrollers on the grid, then connect them together with wires. You will also need to connect microcontrollers to the input and/or output ports located on the grid.  
After you've created a layout, you will need to program the controllers with the `Microcoded Hardware System` (M.H.S. for short), a custom-built programming language, based on the `MCxxxx` language for similar processors.  
Once finished designing your solution, you can test it by walking through tick-by-tick with the `Step` button.  
You can also run through the whole program with the `Advance` button, or try again with the `Reset` button.

# Microcoded Hardware System
The M.H.S. language is relatively simple. Programs are structured into lines, and each line contains one command, followed by one or two arguments, depending on the command.  
Lines may also be prefixed with a conditional operator, which will be detailed later on.  

## Registers
Each microcontroller has two internal data registers. They are:  
- `mhs`: The `mhs` register is used for all arithmetic operations, and for storing other data.  
- `ics`: The `ics` register is a general-purpose register for storing data.  
  
Additionally, all microcontrollers have access to four I/O registers, which are:  
- `in1`: First input register, cannot be written to  
- `in2`: Second input register, cannot be written to  
- `ou1`: First output register  
- `ou2`: Second output register  

## General Commands
Microcontrollers have access to basic commands for managing themselves and their data. They are:  
- <a id="mov"></a>`mov`: Moves a value into a register. 
    - This value can be a numberic literal, or the value within another register
    - Example: 
        ```
        mov in1 mhs
        ```
        would move the value in the `in1` register to the `mhs` register
- <a id="jmp"></a>`jmp`: Jumps to a new line, causing the microcontroller to start executing from that line. 
    - Lines begin at index 0, and go to index 9. Any supplied value over 9 will simply be capped to 9.
    - The supplied value can be either a numeric literal, or the value within a register.
    - Example:
        ```
        jmp 3
        ```
        or 
        ```
        jmp ics
        ```
        would jump to the fourth line, or the line number stored in the `ics` register
- <a id="slp"></a>`slp`: Halts execution of the microcontroller for a supplied number of ticks. 
    - Sleep values of `1` will halt the microcontroller for the remainder of the tick, and resume on the next one.
    - The supplied number can either be a numeric literal, or the value within a register. 
    - Programs should **ALWAYS** have at least one `slp` statement, otherwise they will loop uncontrollably. This is considered undefined behavior, and should be avoided.
    - Example:
        ```
        slp 3
        ```
        would sleep the microcontroller for the remainder of the current tick, and then two ticks after that.

## Arithmetic Commands
Microcontrollers can use a number of commands to do basic mathematical calculations. They are:  
- <a id="add"></a>`add`: Add a provided value to the `mhs` register.  
    - The provided value can be a numeric literal, or the value inside of another register.
    - Example:
        ```
        add 42
        ```
        would add 42 to the current value of `mhs`.
- <a id="sub"></a>`sub`: Does the same thing as `add`, but with subtraction instead   
- <a id="mul"></a>`mul`: Does the same thing as `add`, but with multiplication instead   
*Note:* All arithmetic operations will cause the mhs register to overflow or underflow when going below 0 or above 999. Therefore, if `mhs` contained a value of 995, and `add 15` was called, `mhs` would then contain the value of 11.

## Logical Commands
Microcontrollers have access to various commands used for conditional execution and logic. 
All lines in M.H.S. programs can be prepended with either a `+` or `-` operator.  
These will cause the line to be conditionally executed.  
If the microcontroller's current conditional state is `True`, `+` lines will be enabled, and if the state is `False`, `-` lines will be enabled.
The logical commands are:
- <a id="tis"></a>`tis` (test is): Tests if two values are equal. If they are, conditional state is set to `True`, otherwise it is set to `False` 
    - The values can be either numeric literals, or the values inside registers, or one of each.
    - Example: 
        ```
        tis mhs 3
        ```
        would test if the value inside the `mhs` register is equal to 3, and set the conditional state to the result of that comparison.
- <a id="tgt"></a>`tgt` (test greater than): Tests if a value, `a`, is greater than another value, `b`. If `a` is greater than `b`, conditional state is set to `True`, otherwise it is set to `False` 
    - `a` and `b` can be either numeric literals, or the values inside registers, or one of each.  
    - Example:
        ```
        tgt mhs 10
        ```
        would test if the value inside `mhs` is greater than 10, and set the conditional state to the result of that test.
- <a id="tlt"></a>`tlt` (test lesser than): Tests if a value, `a`, is lesser than another value, `b`. If `a` is lesser than `b`, conditional state is set to `True`, otherwise it is set to `False` 
    - `a` and `b` can be either numeric literals, or the values inside registers, or one of each.  
    - Example:
        ```
        tlt mhs 10
        ```
        would test if the value inside `mhs` is lesser than 10, and set the conditional state to the result of that test.

There is also another command, that functions similarly to arithmetic commands but is focused on logic:  
- <a id="not"></a>`not`: Produces the logical not of a value, and stores the result in the `mhs` register. 
    - The value can be either a numeric literal, or the value inside of a register
    - The logical not of 0 is 1, and the logical not of any other value is 0
    - Example:
        ```
        not 1
        ```
        would take the logical not of 1, which is 0, and store it in the `mhs` register.

## Example Program
```
1 | add 1
2 | mov mhs ics
3 | tis ics 1
4 | + mov ics ou1
5 | - mov 2 ou1
6 | slp 1
```

This example program adds 1 to the `mhs` register, and then moves that value to the `ics` register. It then checks if the `ics` register's value is equal to 1, and if it is, it moves the `ics` value to the first output port. Otherwise, it moves the numeric literal `2` to the first output port. It then sleeps for the rest of the tick.  
  
This would cause the program to output `1` to the output port on the first tick it runs, and then to output `2` on every other tick.