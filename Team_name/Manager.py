import os
import numpy as np
import time
import math
from math import atan2
# Choose names for your players and team
    # Choose a funny name for each player and your team
    # Use names written only in cyrillic
    # Make sure that the name is less than 11 characters
    # Don't use profanity!!!

# Goal posts coordinates
left_goal_upper = (50, 343)
left_goal_lower = (50, 578)
right_goal_upper = (1316, 343)
right_goal_lower = (1316, 578)
middle_of_playground = 460.5
left_goal_area = [350, 150, 560, 50] # North East South West

def team_properties():
    properties = dict()
    player_names = ["Б", "Л", "Г"]
    properties['team_name'] = "Мак Челзи"
    properties['player_names'] = player_names
    properties['image_name'] = 'Red.png' # use image resolution 153x153
    properties['weight_points'] = (15, 40, 15)
    properties['radius_points'] = (5, 11, 0)
    properties['max_acceleration_points'] = (40, 40, 15)
    properties['max_speed_points'] = (40, 10, 25)
    properties['shot_power_points'] = (18, 55, 13)
    return properties

def run_player_to_target(player,i,manager_decision,target_x,target_y):

    dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5
    if dist_target > 5:  
        target_angle = math.atan2(target_y - player['y'], target_x - player['x'])
        manager_decision[i]['alpha'] = target_angle
        manager_decision[i]['force'] = player['a_max'] * player["mass"]  # Maximum acceleration to move quickly
    else:  # If within close range of the target position
        # Stop moving and reset the alpha (direction)
        manager_decision[i]['force'] = 0  
        manager_decision[i]['alpha'] = np.pi


def run_keeper_to_ball_and_shoot(player,i,manager_decision,dist_ball,ball):
    # Move goalkeeper more vertically towards the ball
    target_angle = math.atan2(ball['y'] - player['y'], ball['x'] - player['x'])
    vertical_angle = math.atan2(ball['y'] - player['y'], 75 - player['x'])  # Angle towards vertical
    weighted_angle = 0.5 * target_angle + 0.5 * vertical_angle  # Weighted average of target and vertical angles
    manager_decision[i]['alpha'] = weighted_angle
    manager_decision[i]['force'] = player['a_max'] * player["mass"]

    # Check if goalkeeper touches the ball
    if (player['x']<ball['x']):
    
        manager_decision[i]['shot_request'] = True


# left_goal_upper = (50, 343)
# left_goal_lower = (50, 578)
# right_goal_upper = (1316, 343)
# right_goal_lower = (1316, 578)
def run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball):
    manager_decision[i]['force'] = player['a_max']
    manager_decision[i]['shot_request'] = False
    angle_to_ball = atan2(ball['y'] - player['y'], ball['x'] - player['x'])
    print(dist_ball)
    if dist_ball > 0:
        manager_decision[i]['alpha'] = angle_to_ball
        
    else:
        angle_to_goal = atan2(343 - player['y'], 1316 - player['x'])
        manager_decision[i]['alpha'] = angle_to_goal



def find_coordinates_for_straight_shot(ball, goal_post, distance_to_go_from_ball):
    # Calculate the slope of the line between the ball and the goal post
    dx = goal_post[0] - ball['x']
    dy = goal_post[1] - ball['y']
    if dx != 0:  # Avoid division by zero
        slope = dy / dx
    else:
        slope = float('inf')  # Vertical line
    
    # Determine the sign of the change in x and y based on the quadrant of the goal post relative to the ball
    if dx > 0:
        sign_x = 1
    else:
        sign_x = -1
    
    if dy > 0:
        sign_y = 1
    else:
        sign_y = -1
    
    # Calculate the new coordinates for the player
    new_x = ball['x'] + sign_x * distance_to_go_from_ball / math.sqrt(1 + slope**2)
    new_y = ball['y'] + sign_y * slope * distance_to_go_from_ball / math.sqrt(1 + slope**2)
    
    return new_x, new_y



# This function gathers game information and controls each one of your three players
def decision(our_team, their_team, ball, your_side, half, time_left, our_score, their_score):
    manager_decision = [dict(), dict(), dict()]


    for i in range(3):
        player = our_team[i]
        manager_decision[i]['shot_power'] = player['shot_power_max']
        manager_decision[i]['shot_request'] = False

        
        if i == 2:
            dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
            distance_to_go_from_ball = -(15 + player['radius'])
            target_x, target_y = find_coordinates_for_straight_shot(ball, right_goal_upper, distance_to_go_from_ball)
            run_player_to_target(player, i, manager_decision, target_x, target_y)

        elif i == 1:  # If player is the goalkeeper
            dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
            if ball['x'] < 300:
                # If the ball is under certain other coordinates and the player is in a specific area
                run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball)
            elif ball['x'] < 400 and ball['y'] < middle_of_playground:
                # If the ball is under certain coordinates
                target_x, target_y = 75, middle_of_playground - 50
                run_player_to_target(player, i, manager_decision, target_x, target_y)
            elif ball['x'] < 400 and ball['y'] > middle_of_playground:
                # If the ball is under certain coordinates
                target_x, target_y = 75, middle_of_playground + 50
                run_player_to_target(player, i, manager_decision, target_x, target_y)
            else:
                # Default behavior if ball is not in specific ranges
                target_x, target_y = 75, middle_of_playground
                run_player_to_target(player, i, manager_decision, target_x, target_y)

        elif i == 0: 
            dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
            if ball['x'] < 100 and player['x'] < ball['x']:
                # If the ball is under certain other coordinates and the player is in a specific area
                run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball)
            elif ball['x'] < 400 and ball['y'] < middle_of_playground:
                # If the ball is under certain coordinates
                target_x, target_y = 50, middle_of_playground + 50
                run_player_to_target(player, i, manager_decision, target_x, target_y)
            elif ball['x'] < 400 and ball['y'] > middle_of_playground:
                # If the ball is under certain coordinates
                target_x, target_y = 50, middle_of_playground - 50
                run_player_to_target(player, i, manager_decision, target_x, target_y)
            else:
                target_x, target_y = 700, middle_of_playground - 100
                run_player_to_target(player, i, manager_decision, target_x, target_y)
        else:
            manager_decision[i]['alpha'] = np.pi # player['alpha'] # choose direction for running (0, 2*pi)
            manager_decision[i]['force'] = 0 # accelerate or deaccelerate your player up to 'v_max' or 0: (-0.5 * 'a_max' * 'mass', 'a_max' * 'mass')

                    
                
    return manager_decision