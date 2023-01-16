from gym_multigrid.multigrid import *

class SoccerGameEnv(MultiGridEnv):
    """
    Environment in which the agents have to fetch the balls and drop them in their respective goals
    """

    def __init__(
        self,
        size=10,
        view_size=3,
        width=None,
        height=None,
        goal_pst = [],
        goal_index = [],
        num_balls=[],
        balls_pst = [],
        balls_index=[],
        agents_index = [],
        zero_sum = False,
        reward_value=1,
    ):
        
        self.goal_pst = goal_pst
        self.goal_index = goal_index
        self.num_balls = num_balls
        self.balls_pst = balls_pst
        self.balls_index = balls_index
        self.zero_sum = zero_sum
        self.reward_value = reward_value

        self.world = World

        agents = []
        for i in agents_index:
            agents.append(Agent(self.world, i, view_size=view_size))

        super().__init__(
            grid_size=size,
            width=width,
            height=height,
            max_steps= 50,
            # Set this to True for maximum speed
            see_through_walls=False,
            agents=agents,
            agent_view_size=view_size
        )

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.horz_wall(self.world, 0, 0)
        self.grid.horz_wall(self.world, 0, height-1)
        self.grid.vert_wall(self.world, 0, 0)
        self.grid.vert_wall(self.world, width-1, 0)

        # place goal/nest
        for i in range(len(self.goal_pst)):
            self.place_obj(ObjectGoal(world=self.world,index=self.goal_index[i],target_type='ball',reward=self.reward_value), 
                top=self.goal_pst[i], size=[1,1])

        # place balls
        for number, index in zip(self.num_balls, self.balls_index):
            for i in range(number):
                self.place_obj(Ball(self.world,index), top=self.balls_pst[i], size=[1,1])

        # Randomize the player start position and orientation
        for a in self.agents:
            self.place_agent(a)

    def _reward(self, i, rewards, reward=1):
        for j,a in enumerate(self.agents):
            #if a.index==i or a.index==0:
            if j == i:
                rewards[i]+=reward
                #print("I got reward cause I am of the same index", a.index)
                #print("I am agent {} and got this reward: {}".format(i, rewards[i]))
            '''if self.zero_sum:
                if a.index!=i or a.index==0:
                    rewards[j] -= reward'''

    def _handle_pickup(self, i, rewards, fwd_pos, fwd_cell):
        if fwd_cell:
            if fwd_cell.can_pickup():
                if self.agents[i].carrying is None:
                    self.agents[i].carrying = fwd_cell
                    self.agents[i].carrying.cur_pos = np.array([-1, -1])
                    self.grid.set(*fwd_pos, None)
            elif fwd_cell.type=='agent':
                if fwd_cell.carrying:
                    if self.agents[i].carrying is None:
                        self.agents[i].carrying = fwd_cell.carrying
                        fwd_cell.carrying = None

    def _handle_drop(self, i, rewards, fwd_pos, fwd_cell):
        if self.agents[i].carrying:
            if fwd_cell:
                #if fwd_cell.type == 'objgoal' and fwd_cell.target_type == self.agents[i].carrying.type:
                if fwd_cell.type == 'objgoal':
                    if self.agents[i].carrying.index in [0, fwd_cell.index]:
                        #print("I am carrying agent {} and got this reward: {}".format(i, fwd_cell.reward))
                        #rewards[i]+=fwd_cell.reward
                        #self._reward(fwd_cell.index, rewards, fwd_cell.reward)
                        self._reward(i, rewards, fwd_cell.reward)
                        self.agents[i].carrying = None

                elif fwd_cell.type=='agent': #pasar la bola
                    if fwd_cell.carrying is None:
                        fwd_cell.carrying = self.agents[i].carrying
                        self.agents[i].carrying = None
            else:
                self.grid.set(*fwd_pos, self.agents[i].carrying)
                self.agents[i].carrying.cur_pos = fwd_pos
                self.agents[i].carrying = None


    def step(self, actions):
        obs, rewards, done, info = MultiGridEnv.step(self, actions)
        return obs, rewards, done, info


class SoccerGame4HEnv10x15N2(SoccerGameEnv):
    def __init__(self):
        super().__init__(size=None,
        height=11,
        width=15,
        goal_pst = [[1,5]], # x,y coordinates of the goal -- topleft corner is the 0,0
        goal_index = [1], # GOAL COLOR - particular number refer to team color - 0:red, 1:green, 2:blue
        num_balls=[4],
        balls_pst = [[5,6], [1,6], [2,6], [5,5]], # x,y coordinates of the goal -- topleft corner is the 0,0
        balls_index=[0], #changes ball color - 0:red, 1:green, 2:blue
        agents_index = [1,2,3,4], #NUMBER OF AGENTS - particular number refer to team color - 0:red, 1:green, 2:blue
        zero_sum=True,
        reward_value=2)

