## ----------------------------------------------------------------------------------------------------------
## TEMPLATE
## Please DO NOT change the naming convention within this template. Some changes may
## lead to your program not functioning as intended.

import time
import random
import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)


## STUDENT CODE BEGINS
## ----------------------------------------------------------------------------------------------------------
## Example to rotate the base: arm.rotateBase(90)

'''
1P13 Project 2
Dec 2nd, 2020
Tues-28 Computing subteam:
    Luigi Quattrociocchi (quattrl)
    Hetash Rattu (rattuh)
'''



'''NECESSARY CONSTANT VARIABLES'''

EMG_THRESHOLD = 0.4                         # 0-1 muscle sensor value 
DELAY = 3.0                                 # number of seconds between commands
SMALL_GRIP = 28.4                           # angle for containers 1-3
LARGE_GRIP = 23.3                           # angle for containers 4-6

HOME_LOCATION = [0.4064, 0.0, 0.4826]       # effector position at arm.home()
PICK_UP_LOCATION = [0.4989, 0.003, 0.0408]  # effector position of container



'''BEGIN FUNCTION DEFINITIONS'''

def identify_autoclave_bin_location(container_id):
    '''
    Returns a list with 3 elements describing x, y, z coordinates of the
    location of an autoclave bin that corresponds to the given container id

    Parameters:
        container_id (int): the id of the desired container (1-6)

    Returns:
        a list of floats of length 3 containing location coordinates
    '''

    if container_id == 1: # small red
        return [-0.5711, 0.229, 0.4218]
    if container_id == 2: # small green
        return [0.0, -0.6253, 0.4072]
    if container_id == 3: # small blue
        return [0.0, 0.6253, 0.4072]
    
    if container_id == 4: # large red
        return [-0.3481, 0.1442, 0.3303]
    if container_id == 5: # large green
        return [0.0, -0.3886, 0.3638]
    if container_id == 6: # large blue
        return [0.0, 0.3886, 0.3638]

    # base case home location
    return HOME_LOCATION


def move_end_effector(x, y, z):
    '''
    Waits for the correct configuration of emg sensor values (left arm
    flexed above the threshold and right arm fully extended), then moves
    the arm to the specified x, y, z coordinate location.

    Parameters:
        x (float): x coordinate location of the end effector
        y (float): y coordinate location of the end effector
        z (float): z coordinate location of the end effector

    Returns: None
    '''
    
    # remind the user
    print("MOVE: FLEX LEFT ONLY")

    # wait for left flexed and right extended
    while True:
        left_value =  arm.emg_left()
        right_value = arm.emg_right()
        
        if left_value > EMG_THRESHOLD and \
           right_value == 0:

            # move arm to specified location
            arm.move_arm(x, y, z)

            # terminate the function
            break


def control_gripper(to_open, container_id):
    '''
    Waits for the correct configuration of emg sensor values (right arm
    flexed above the threshold and left arm fully extended), then opens
    or closes the gripper based on the given to_open boolean flag by an
    amount that is determined by the container size.

    Parameters:
        to_open (bool): should gripper be opened (True) or closed (False)
        container_id (int): the id of the desired container (1-6)
    
    Returns: None
    '''

    # determine what grip angle to use based on container size
    is_small = 1 <= container_id <= 3
    grip_amount = SMALL_GRIP if is_small else LARGE_GRIP
    
    # determine if gripper should be opened or closed
    grip_amount = -grip_amount if to_open else grip_amount
    
    # remind the user
    print("GRAB: FLEX RIGHT ONLY")
    
    # wait for right flexed and left extended
    while True:
        left_value =  arm.emg_left()
        right_value = arm.emg_right()
        
        if right_value > EMG_THRESHOLD and \
           left_value == 0:

            # change gripper angle by predetermined grip amount
            arm.control_gripper(grip_amount)
            
            # terminate the function
            break


def open_autoclave_drawer_bin(to_open, container_id):
    '''
    Waits for the correct configuration of emg sensor values (both left
    and right arms flexed above the threshold). After waiting it will
    check if the container is a large size and should continue (id 4-6).
    Then based on the to_open boolean flag will open or close the drawer
    which corresponds to the color of the container.

    Parameters:
        to_open (bool): should drawer be opened (True) or closed (False)
        container_id (int): the id of the desired container (1-6)
    
    Returns: None
    '''

    # determine container size based on container id
    is_large = 4 <= container_id <= 6

    # terminate the function immediately if container is small
    if not is_large:
        return

    # remind the user
    print("OPEN: FLEX BOTH ARMS")

    # wait for left and right both flexed
    while True:
        left_value =  arm.emg_left()
        right_value = arm.emg_right()

        if left_value > EMG_THRESHOLD and \
            right_value > EMG_THRESHOLD:

            # open or close drawer based on color
            if container_id == 4: # large red
                arm.open_red_autoclave(to_open)
            if container_id == 5: # large green
                arm.open_green_autoclave(to_open)
            if container_id == 6: # large blue
                arm.open_blue_autoclave(to_open)

            # terminate the function
            break


def main():
    '''
    The main logic and execution of task. This function will choose the
    ids of containers 1 to 6 in a random order and perform a full cycle
    of spawn, pick up, transfer, drop off, and home operations for each
    of them. There are no parameters or return values.
    '''

    # return to home before beginning
    # assume environment has been reset
    arm.home()
    time.sleep(DELAY)


    # initializes a list of containers from 1 to 6 inclusive
    containers = list(range(1, 7))
    # randomly shuffles the list of ids.
    random.shuffle(containers)

    # iterates over shuffled list of container ids
    for container in containers:
        '''
        a single cycle will do the following:
            spawn container
            pick up container
            transfer container
            drop off container
            return to home
        
        some delay is added between each command
        '''
        
        # spawn
        arm.spawn_cage(container)
        time.sleep(DELAY)
        
        # pick up
        move_end_effector(*PICK_UP_LOCATION)
        time.sleep(DELAY)
        control_gripper(False, container)
        time.sleep(DELAY)
        move_end_effector(*HOME_LOCATION)
        time.sleep(DELAY)

        # transfer
        open_autoclave_drawer_bin(True, container)
        time.sleep(DELAY)
        move_end_effector(*identify_autoclave_bin_location(container))
        time.sleep(DELAY)

        # drop off
        control_gripper(True, container)
        time.sleep(DELAY)
        
        # return home
        move_end_effector(*HOME_LOCATION)
        time.sleep(DELAY)
        open_autoclave_drawer_bin(False, container)
        time.sleep(DELAY)


    # program is finished
    print("DONE")




'''MAIN EXECUTION'''

if __name__ == '__main__':
    main()
