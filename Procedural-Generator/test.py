import numpy as np
import utils
t_set = [];
t_class = [];
t_set,t_class = utils.glob_data("dataset/structure",t_set,t_class,[1,0,0]);
t_set,t_class = utils.glob_data("dataset/flora",t_set,t_class,[0,1,0]);
t_set,t_class = utils.glob_data("dataset/terrain",t_set,t_class,[0,0,1]);
t_set = np.array(t_set);
t_class = np.array(t_class);

print(len(t_set));