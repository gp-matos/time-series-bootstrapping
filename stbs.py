import numpy as np
from manim import *



class STBS(Scene):
    def construct(self):

        #generating data
        np.random.seed(123)
        self.data = np.random.randn(100)
        self.t = range(len(self.data))
        self.LENGTH = len(self.data)
        self.PROB = .06

        #generates the first axes at the beginning
        axes = Axes(
            x_range=[0, 105],
            y_range=[-5, 5],
            axis_config={"include_ticks": False},
            tips=True,
        )

        #initially plots the original data
        series_plot = axes.plot_line_graph(
            x_values=self.t,
            y_values=self.data, 
            line_color=BLUE,
            vertex_dot_radius=0.0833,
        )


        orig_series_grp = VGroup(axes, series_plot)
        #shrinks and moves the original data to the top left corner
        small_series = orig_series_grp.copy().scale(0.6).to_corner(UL).shift(RIGHT*0.5)

        #this sections creates the text objects on the top right corner
        I_rv = Tex(f"I \(\sim \) Uniform(0, {len(self.data)})")
        L_rv = Tex(f"L \(\sim \) Geometric(p)").next_to(I_rv, DOWN)
        text_grp = VGroup(I_rv, L_rv)

        I_txt = Tex(f"I =")
        L_txt = Tex(f"L =").next_to(I_txt, DOWN)
        p_txt = Tex(f"p =").next_to(L_txt, DOWN)
        text_grp_corner = VGroup(I_txt, L_txt, p_txt).to_corner(UR).shift(LEFT*1.6).shift(DOWN*.7)

        
        ######################################## INITIAL ANIMATION ########################################
        title = Title("stationary bootstrap", include_underline=False).to_edge(UP)
        self.play(Write(title))
        self.add(title)

        self.play(Create(text_grp))
        self.wait(1)
        self.play(Transform(text_grp, text_grp_corner))

        self.play(Create(axes))
        self.play(Create(series_plot["line_graph"]), *[Create(dot) for dot in series_plot['vertex_dots']])
        #self.play(Create(series_plot["line_graph"]), Create(series_plot['vertex_dots'][20]))
        self.wait(1)
        self.play(Transform(orig_series_grp, small_series))
        self.wait()
        ####################################################################################################


        #this section creates the integer and decimal number objects for I, L, and p
        I_val_obj = Integer(0).next_to(I_txt, RIGHT, buff=0.2)
        L_val_obj = Integer(0).next_to(L_txt, RIGHT, buff=0.2)

        P_val = self.PROB
        P_val_obj = DecimalNumber(P_val).next_to(p_txt, RIGHT, buff=0.2)
        #P_val_obj.add_updater(lambda m: m.set_value(P_val))
        np.random.seed(10)
        def randomize_I(I_val_obj):
            I = np.random.randint(0, len(self.data))
            I_val_obj.set_value(I)
        def randomize_L(L_val_obj):
            L = np.random.geometric(self.PROB)
            L_val_obj.set_value(L)
   
        self.play(Create(I_val_obj), Create(L_val_obj), Create(P_val_obj))

        #generates the axis for the bootstrap sample
        bootstrap_axes = Axes(
            x_range=[0, 105],
            y_range=[-4, 4],
            axis_config={"include_ticks": False},
            tips=True,
        ).scale(0.6).to_corner(DL).shift(RIGHT*0.5)

        #function for generating a block from the original data
        def gen_block(X, I, L):
            if I + L > len(X):
                #wrap around
                return np.concatenate((X[I:], X[:I+L-len(X)]))
            else:
                return X[I:I+L]
        
        #animates the bootstrap axis and sets initial params for the loop
        self.play(Create(bootstrap_axes))
        bs_index = 0
        blocks = []
        block_plots = VGroup()
        i = 0
        #loops until the bootstrap sample is complete
        sum = 0 ### testing purposes
        while bs_index < self.LENGTH:
            #updates the values of I, L, and p
            self.play(UpdateFromFunc(I_val_obj, randomize_I), UpdateFromFunc(L_val_obj, randomize_L))
            I = I_val_obj.get_value()
            L = L_val_obj.get_value()
            self.wait(1)
            #creates the block label
            block_label = Tex(f"$B_{{{I},{L}}}$").next_to(bootstrap_axes, RIGHT, buff=2.5)
            block_label_mutated = Tex(f"$B_{{{i+1}}}^*$").next_to(bootstrap_axes, RIGHT, buff=2.5)
            self.play(Create(block_label))

            #logic for wrapping around the data
            if I + L > len(self.data):
                #wrap around
                block_plot_origin_end = small_series[0].plot_line_graph(
                    x_values=range(I, len(self.data)),
                    y_values=self.data[I:], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                block_plot_origin_begin = small_series[0].plot_line_graph(
                    x_values=range(I+L-len(self.data)),
                    y_values=self.data[:I+L-len(self.data)], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                block_plot_origin_begin_shifted = small_series[0].plot_line_graph(
                    x_values=range(len(self.data), I+L),
                    y_values=self.data[:I+L-len(self.data)], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                #if you wrap around, move the part that wrapped back up to the front
                fin_block = VGroup(block_plot_origin_end, block_plot_origin_begin_shifted)
                self.play(Create(block_plot_origin_end["line_graph"]), *[Create(dot) for dot in block_plot_origin_end['vertex_dots']])
                self.play(Create(block_plot_origin_begin["line_graph"]), *[Create(dot) for dot in block_plot_origin_begin['vertex_dots']])
                self.play(ReplacementTransform(block_plot_origin_begin, block_plot_origin_begin_shifted))
            else:
                block_plot_origin_end = small_series[0].plot_line_graph(
                    x_values=range(I, I+L),
                    y_values=self.data[I:I+L], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                self.play(Create(block_plot_origin_end["line_graph"]), *[Create(dot) for dot in block_plot_origin_end['vertex_dots']])
                fin_block = block_plot_origin_end
                block_plot_origin_begin_shifted = None #this is just to avoid an error later

            #get the actual data for the bootstrap block and add to the blocks array    
            block_sample = gen_block(self.data, I, L)
            sum += len(block_sample)
            print(sum) ### testing purposes
            blocks.append(block_sample)

            #make a plot figure for the individual block
            block_plot = bootstrap_axes.plot_line_graph(
                x_values=range(bs_index, bs_index+L),
                y_values=list(block_sample), 
                line_color=RED,
                vertex_dot_radius=0.05,
            )
            #add the block plot to the group of block plots (these are different than list of the actual data)
            # copied = block_plot.copy()
            block_plots.add(block_plot)

            self.wait()
            self.play(Transform(block_label, block_label_mutated))
            self.play(ReplacementTransform(fin_block.copy(), block_plot))
            if block_plot_origin_begin_shifted != None:
                self.play(
                    FadeOut(fin_block),
                    FadeOut(block_label), 
                )
            else:
                self.play(
                    FadeOut(fin_block),
                    FadeOut(block_label), 
                )
            bs_index += L
            i += 1

        #combine the arrays in blocks into one numpy array
        bootstrap_sample = np.concatenate(blocks)
        print("=====================================") ### testing purposes
        print(len(bootstrap_sample)) ### testing purposes
        bootstrap_sample = bootstrap_sample[:self.LENGTH]
        print(len(bootstrap_sample)) ### testing purposes
        #plot the final bootstrap sample
        fin_bootstrap_plot = bootstrap_axes.plot_line_graph(
            x_values=range(self.LENGTH),
            y_values=bootstrap_sample, 
            line_color=GREEN,
            vertex_dot_radius=0.05,
        )
        
        self.play(Create(fin_bootstrap_plot["line_graph"]), *[Create(dot) for dot in fin_bootstrap_plot['vertex_dots']])
        self.play(FadeOut(block_plots))
        self.wait(3)

        


class MBB(Scene):
    def construct(self):

        #generating data
        np.random.seed(123)
        self.data = np.random.randn(100)
        self.t = range(len(self.data))
        self.LENGTH = len(self.data)
        self.b = 10

        #generates the first axes at the beginning
        axes = Axes(
            x_range=[0, 105],
            y_range=[-5, 5],
            axis_config={"include_ticks": False},
            tips=True,
        )

        #initially plots the original data
        series_plot = axes.plot_line_graph(
            x_values=self.t,
            y_values=self.data, 
            line_color=BLUE,
            vertex_dot_radius=0.0833,
        )


        orig_series_grp = VGroup(axes, series_plot)
        #shrinks and moves the original data to the top left corner
        small_series = orig_series_grp.copy().scale(0.6).to_corner(UL).shift(RIGHT*0.5)

        #this sections creates the text objects on the top right corner
        I_rv = Tex(f"I \(\sim \) Uniform(0, {len(self.data)})")
        b_rv = Tex(f"b = block size").next_to(I_rv, DOWN)
        text_grp = VGroup(I_rv, b_rv)

        I_txt = Tex(f"I =")
        b_txt = Tex(f"b =").next_to(I_txt, DOWN)
        text_grp_corner = VGroup(I_txt, b_txt).to_corner(UR).shift(LEFT*1.6).shift(DOWN*.7)

        
        ######################################## INITIAL ANIMATION ########################################
        title = Title("Moving Blocks Bootstrap", include_underline=False).to_edge(UP)
        self.play(Write(title))
        self.add(title)

        self.play(Create(text_grp))
        self.wait(1)
        self.play(ReplacementTransform(text_grp, text_grp_corner))

        self.play(Create(axes))
        self.play(Create(series_plot["line_graph"]), *[Create(dot) for dot in series_plot['vertex_dots']])
        #self.play(Create(series_plot["line_graph"]), Create(series_plot['vertex_dots'][20]))
        self.wait(1)
        self.play(ReplacementTransform(orig_series_grp, small_series))
        self.wait()
        ####################################################################################################


        #this section creates the integer and decimal number objects for I, L, and p
        I_val_obj = Integer(0).next_to(I_txt, RIGHT, buff=0.2)
        b_val_obj = Integer(10).next_to(b_txt, RIGHT, buff=0.2)
        np.random.seed(10)
        def randomize_I(I_val_obj):
            I = np.random.randint(0, len(self.data))
            I_val_obj.set_value(I)
   
        self.play(Create(I_val_obj), Create(b_val_obj))

        #generates the axis for the bootstrap sample
        bootstrap_axes = Axes(
            x_range=[0, 105],
            y_range=[-4, 4],
            axis_config={"include_ticks": False},
            tips=True,
        ).scale(0.6).to_corner(DL).shift(RIGHT*0.5)

        
        #function for generating a block from the original data
        def gen_block(X, I, L):
            if I + L > len(X):
                #dont wrap around for moving blocks
                return X[I:len(X)]
            else:
                return X[I:I+L]
        
        #animates the bootstrap axis and sets initial params for the loop

        dot = Dot(color=ORANGE).move_to(small_series[0].c2p(I_val_obj.get_value(), -3.5))
        dot.add_updater(lambda m: m.move_to(small_series[0].c2p(I_val_obj.get_value(), -3.5)))

        self.play(Create(dot), Create(dot.copy().next_to(I_val_obj, RIGHT, buff=0.2)))


        self.play(Create(bootstrap_axes))
        
        bs_index = 0
        blocks = []
        block_plots = VGroup()
        i = 0
        #loops until the bootstrap sample is complete
        sum = 0 ### testing purposes
        while bs_index < self.LENGTH:
            #updates the values of I, L, and p
            self.play(UpdateFromFunc(I_val_obj, randomize_I))
            I = I_val_obj.get_value()
            self.wait(1)
            # line = Line(dot, small_series[0].c2p(I_val_obj, -3.5)).move_to(small_series[0].c2p(I_val_obj, -3.5))
            #creates the block label
            block_label = Tex(f"$B_{{{I},10}}$").next_to(bootstrap_axes, RIGHT, buff=2.5)
            block_label_mutated = Tex(f"$B_{{{i+1}}}^*$").next_to(bootstrap_axes, RIGHT, buff=2.5)
            self.play(Create(block_label))

            #logic for wrapping around the data
            if I + self.b > len(self.data):
                #cut off the end of the data
                block_plot_origin_end = small_series[0].plot_line_graph(
                    x_values=range(I, len(self.data)),
                    y_values=self.data[I:], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                #if you wrap around, move the part that wrapped back up to the front
                fin_block = block_plot_origin_end #try making this a copy instead
                self.play(Create(block_plot_origin_end["line_graph"]), *[Create(dot) for dot in block_plot_origin_end['vertex_dots']])
            else:
                block_plot_origin_end = small_series[0].plot_line_graph(
                    x_values=range(I, I+self.b),
                    y_values=self.data[I:I+self.b], 
                    line_color=RED,
                    vertex_dot_radius=0.05,
                )
                self.play(Create(block_plot_origin_end["line_graph"]), *[Create(dot) for dot in block_plot_origin_end['vertex_dots']])
                fin_block = block_plot_origin_end #try making this a copy instead

            #get the actual data for the bootstrap block and add to the blocks array    
            block_sample = gen_block(self.data, I, self.b)
            sum += len(block_sample)
            print(sum) ### testing purposes
            blocks.append(block_sample)

            #make a plot figure for the individual block
            block_plot = bootstrap_axes.plot_line_graph(
                x_values=range(bs_index, bs_index+len(block_sample)),
                y_values=list(block_sample), 
                line_color=RED,
                vertex_dot_radius=0.05,
            )
            #add the block plot to the group of block plots (these are different than list of the actual data)
            block_plots.add(block_plot)

            self.wait()
            self.play(Transform(block_label, block_label_mutated))
            self.play(ReplacementTransform(fin_block.copy(), block_plot))
            self.play(FadeOut(fin_block), FadeOut(block_label))
            bs_index += len(block_sample)
            i += 1

        #combine the arrays in blocks into one numpy array
        bootstrap_sample = np.concatenate(blocks)
        print("=====================================") ### testing purposes
        print(len(bootstrap_sample)) ### testing purposes
        bootstrap_sample = bootstrap_sample[:self.LENGTH]
        print(len(bootstrap_sample)) ### testing purposes
        #plot the final bootstrap sample
        fin_bootstrap_plot = bootstrap_axes.plot_line_graph(
            x_values=range(self.LENGTH),
            y_values=bootstrap_sample, 
            line_color=GREEN,
            vertex_dot_radius=0.05,
        )
        
        self.play(FadeOut(block_plots))
        self.play(Create(fin_bootstrap_plot["line_graph"]), *[Create(dot) for dot in fin_bootstrap_plot['vertex_dots']])
        self.wait(3)