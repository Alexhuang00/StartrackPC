import matplotlib.pyplot as plt

def center_distrubute(actual_center, theory_center):
    avg_actual_y = sum(y for x, y in actual_center) / len(actual_center)
    avg_theory_y = sum(y for x, y in theory_center) / len(theory_center)

    avg_actual_x = sum(x for x, y in actual_center) / len(actual_center)
    avg_theory_x = sum(x for x, y in theory_center) / len(theory_center)

    center_shift_x = avg_theory_x - avg_actual_x
    center_shift_y = avg_theory_y - avg_actual_y

    x1, y1 = zip(*actual_center)
    x2, y2 = zip(*theory_center)

    plt.figure(figsize=(8, 6))
    plt.scatter(x1, y1, color='green', label='actual center', alpha=0.7)
    plt.scatter(x2, y2, color='red', label='theory center', alpha=0.7)
    plt.axhline(y=avg_actual_y, color='green', linestyle='--', linewidth=2,)
    plt.axhline(y=avg_theory_y, color='red', linestyle='--', linewidth=2, label=f'Average shift y= {center_shift_y:.3f}pix')
    plt.vlines(x=avg_actual_x, ymin=490, ymax=510, color='green', linestyle='--', linewidth=2)
    plt.vlines(x=avg_theory_x, ymin=490, ymax=510, color='red', linestyle='--', linewidth=2, label=f'Average shift x= {center_shift_x:.3f}pix')

    

    plt.xlabel('X-axis')
    plt.ylabel('Y-axis (increasing downward)')
    plt.title('Distribution of observed, theory center (Y reversed)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.gca().invert_yaxis()  # Reverse y-axis here
    plt.savefig("/home/alex/Startrack/06Figure/center_ditribution(pix).png", dpi=300)


def solve_time(solving_time):

    indices = list(range(len(solving_time)))
    avg = sum(solving_time)/len(solving_time)

    plt.figure(figsize=(10, 6))
    plt.bar(indices, solving_time, color='red', edgecolor='black', label='astrometry.net')
    plt.axhline(y=avg, color='red', linestyle='--', linewidth=2, label=f'Average(0~n) = {avg:.3f}s')

    plt.xlabel('i')
    plt.ylabel('Solve Time (seconds)')
    plt.title('Solve Time per image with Average Line')
    plt.xticks(indices)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("/home/alex/Startrack/06Figure/solve_time.png", dpi=300)

def earthloc_distrubute(actual_loc, lulin_loc, correct):

    x1, y1 = zip(*actual_loc)
    (x2, y2) = lulin_loc

    plt.figure(figsize=(8, 6))
    plt.scatter(x1, y1, color='green', label='solved loc', alpha=0.7)
    plt.scatter(x2, y2, color='red', label='true loc(120.872624, 23.469447)', alpha=0.7)

    plt.xlabel('longtitude')
    plt.ylabel('latitude')
    plt.title('Distribution of observed, theory location')
    plt.legend()
    plt.grid(True)

    if correct:
        plt.savefig("/home/alex/Startrack/06Figure/solving_result(corrected).png", dpi=300)
    else:
        plt.savefig("/home/alex/Startrack/06Figure/solving_result.png", dpi=300)
    
    
