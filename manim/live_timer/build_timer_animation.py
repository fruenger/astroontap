from manim import *
import numpy as np
from matplotlib import colormaps
from functools import partial

total_time = 60. # sec

class TimeVisSector():

    def __init__(self, value_to_track):
        
        self.outer_radius = 3.5
        self.inner_radius = 3.
        self.start_angle  = 0.
        self.angle        = 0.
        
        self.mobject = Sector()
        self.value_to_track = value_to_track

    def moving_sector(self, **kwargs):
        """Allowed kawrgs are:
        normalization: A function scalar map that converts the tracher value to corresponding number of revolutions
        angle: The angle in degrees determining how long the arc curser itself is
        offset_angle: The aangle which refers to a full revolution
        """
        
        if "offset_angle" in kwargs.keys():
            offset_angle = kwargs["offset_angle"]
        else:
            offset_angle = 0.
        
        if "normalization" in kwargs.keys():
            normalization = kwargs["normalization"]
            use_normalization = True
        else:
            use_normalization = False
            
        def update_mobject(mobject:Sector):
            
            if use_normalization:
                normalized_value = normalization(self.value_to_track.get_value())
            else:
                normalized_value = self.value_to_track.get_value()
            
            mobject.become(Sector(
                outer_radius=self.outer_radius,
                inner_radius=self.inner_radius,
                start_angle=normalized_value * 360. * DEGREES + offset_angle,
                angle=45. * DEGREES,
                fill_opacity=1.
            ))
        
        self.mobject.add_updater(update_mobject)



class timer_animation(MovingCameraScene):
    
    def construct(self):
        
        time = ValueTracker(0)
        
        Ngalaxies = 500
        galaxies = []
        for i in range(Ngalaxies):
            
            pos_x, pos_y = np.random.uniform(-1., 1., 2)
            
            pos_x *= 8.
            pos_y *= 5.
            
            circularity = np.random.uniform(0.25, 1.)
            size = np.random.exponential(0.125)
            
            galaxies.append(Ellipse(
                    size, circularity*size,
                    color=WHITE,
                    stroke_width=0,
                    fill_opacity=0.5
                ).rotate(
                    np.random.uniform(0., 180.) * DEGREES
                ).move_to(
                    [pos_x, pos_y, 0]
                )
            )
        
        anim_group = AnimationGroup(*[DrawBorderThenFill(galaxy) for galaxy in galaxies], lag_ratio=0.01, run_time=total_time)
        time_visualizer = Arc(radius=3, start_angle=0, angle=0. * DEGREES)


        
        time_text       = Text("%.1f" % time.get_value())
        
        time.add_updater(lambda mobject, dt: mobject.increment_value(dt))
        self.add(time)
        # Build the time monitor
        def fill_pie_chart(mobject):
            mobject = mobject.become(Sector(outer_radius=3.5, inner_radius=3., start_angle=0, angle=time.get_value() / total_time * 360. * DEGREES, fill_opacity=1., arc_center=ORIGIN))
            mobject.set_color(ManimColor(colormaps["viridis"](time.get_value() / total_time)))

        def update_text_label(mobject:Text, dt):
            # check if we entered the last 10 seconds ...
            if total_time - time.get_value() >= 9.95:
                mobject.become(Text("%.0f" % np.clip(total_time - time.get_value(), 0., total_time))).scale(3)
                
            elif total_time - time.get_value() > 0.:
                mobject.become(Text("%.1f" % np.clip(total_time - time.get_value(), 0., total_time))).scale(3)
                mobject.set_color(RED)
            
            else:
                mobject.become(Text("0")).scale(3)
                mobject.set_color(RED)
                mobject.scale(1. + (time.get_value() - total_time))
                mobject.set_opacity(np.exp(-2. * (time.get_value() - total_time)))
                

        sector_radii = np.linspace(2., 3., 5)
        
        for sector_radius in sector_radii:

            second_timer = TimeVisSector(time)
            second_timer.outer_radius = sector_radius
            second_timer.inner_radius = sector_radius - 0.1
            
            def normalization(x, speed):
                return speed * x
            second_timer.moving_sector(normalization=partial(normalization, speed=0.5/sector_radius), offset_angle=np.random.uniform(0., 360.))
            self.add(second_timer.mobject)



        time_visualizer.add_updater(fill_pie_chart)
        time_text.add_updater(update_text_label)
        self.add(time_visualizer, time_text)
        self.play(anim_group)
        self.play(FadeIn(Rectangle(BLACK, height=10, width=16, fill_opacity=1.), run_time=6))