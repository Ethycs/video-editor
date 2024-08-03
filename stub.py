# stub.py
import cairo
import math
import numpy as np
import multiprocessing as mp
import imageio
import json
import sys

# Define your constants here
WIDTH = 800
HEIGHT = 600
BG_COLOR = (0.1, 0.1, 0.1)
SPIRAL_COLOR = (0.9, 0.9, 0.9)
THROB_SPEED = 2
ZOOM = 0.5
SPIN_SPEED = 0.5

def create_spiral_frame(time):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Fill background
    ctx.set_source_rgb(*BG_COLOR)
    ctx.paint()

    for x in range(WIDTH):
        for y in range(HEIGHT):
            truPos_x = (x / WIDTH - 0.5) * 2
            truPos_y = (y / HEIGHT - 0.5) * 2 * (HEIGHT / WIDTH)

            angle = math.atan2(truPos_y, truPos_x)
            dist = math.pow((truPos_x**2 + truPos_y**2)**0.5, 0.4 + math.sin((time + math.cos(time * 0.05) * 0.1) * THROB_SPEED) * 0.2)

            spi_factor = math.pow(math.sin(angle + dist * 40 * ZOOM - time * 5 * SPIN_SPEED) + 1.0, 50)
            spi_factor = max(0, min(spi_factor, 1))

            r = SPIRAL_COLOR[0] * (1 - spi_factor) + BG_COLOR[0] * spi_factor
            g = SPIRAL_COLOR[1] * (1 - spi_factor) + BG_COLOR[1] * spi_factor
            b = SPIRAL_COLOR[2] * (1 - spi_factor) + BG_COLOR[2] * spi_factor

            ctx.set_source_rgb(r, g, b)
            ctx.rectangle(x, y, 1, 1)
            ctx.fill()

    # Convert Cairo surface to numpy array
    buf = surface.get_data()
    data = np.ndarray(shape=(HEIGHT, WIDTH, 4), dtype=np.uint8, buffer=buf)
    return data[:, :, [2, 1, 0]]  # Convert BGRA to RGB

def create_frame_wrapper(args):
    time, _ = args
    return create_spiral_frame(time)

def create_animation_parallel(output_file, format='mp4', num_processes=None):
    if num_processes is None:
        num_processes = mp.cpu_count()

    pool = mp.Pool(processes=num_processes)
    
    times = [(i * 0.1, i) for i in range(60)]
    
    frames = pool.map(create_frame_wrapper, times)

    pool.close()
    pool.join()

    if format == 'mp4':
        with imageio.get_writer(output_file, fps=30) as writer:
            for frame in frames:
                writer.append_data(frame)
    elif format == 'gif':
        imageio.mimsave(output_file, frames, fps=30)
    else:
        raise ValueError("Unsupported format. Choose 'mp4' or 'gif'.")

    print(json.dumps({"status": "complete", "output_file": output_file}))

if __name__ == "__main__":
    output_file = sys.argv[1]
    format = sys.argv[2]
    create_animation_parallel(output_file, format)