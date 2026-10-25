/* Original teaching code: CC0-1.0. */
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <assert.h>

static int samples[3] = {10, 20, 30};
static int *pick(int i)
{
    return &samples[i];
}
static size_t param_size(int a[3])
{
    return sizeof a;
}
static size_t grid_param(int a[2][3])
{
    return sizeof *a;
}
static int via_function(int f(int), int i)
{
    return f(i);
}
static int value_at(int i)
{
    return samples[i];
}
int main(void)
{
    int grid[2][3] = {
        {10, 20, 30}, {40, 50, 60}
    };
    int *p = samples;
    int *links[3] = {
        &samples[2], &samples[0],
        &samples[1]
    };
    int (*row)[3] = &samples;
    int (*rows)[3] = grid;
    int *element = grid[0];
    int *(*reader)(int) = pick;
    int (*value)(int) = value_at;
    typedef int Row[3];
    typedef int *Reader(int);
    typedef int *IntPtr;
    Row *alias_row = &samples;
    Reader *alias_reader = pick;
    const IntPtr fixed = samples;
    *fixed = 11;
    int fixed_write = samples[0];
    *fixed = 10;
    assert((*row)[1] == *p + 10);
    assert(*reader(1) == samples[1]);
    assert((*alias_row)[1] == 20);
    assert(*alias_reader(1) == 20);
    printf("{\n");
    printf("\"stdc\":%ld,\n", __STDC_VERSION__);
    printf("\"char_bit\":%d,\n", CHAR_BIT);
    printf("\"samples\":[%d,%d,%d],\n",
        samples[0], samples[1], samples[2]);
    printf("\"grid\":[[%d,%d,%d],[%d,%d,%d]],\n",
        grid[0][0], grid[0][1], grid[0][2],
        grid[1][0], grid[1][1], grid[1][2]);
    printf("\"links_indices\":[%td,%td,%td],\n",
        links[0]-samples, links[1]-samples,
        links[2]-samples);
    printf("\"links_values\":[%d,%d,%d],\n",
        *links[0], *links[1], *links[2]);
    printf("\"sample_count\":%zu,\n",
        sizeof samples / sizeof samples[0]);
    printf("\"int_bytes\":%zu,\n", sizeof(int));
    printf("\"array_bytes\":%zu,\n", sizeof samples);
    printf("\"pointer_bytes\":%zu,\n", sizeof p);
    printf("\"links_bytes\":%zu,\n", sizeof links);
    printf("\"row_pointer_bytes\":%zu,\n", sizeof row);
    printf("\"row_bytes\":%zu,\n", sizeof *row);
    printf("\"param_bytes\":%zu,\n", param_size(samples));
    printf("\"grid_param_row_bytes\":%zu,\n", grid_param(grid));
    /* Steps are computed in element units; no unrelated
       object pointer subtraction or function-pointer cast. */
    printf("\"p_step_elements\":%td,\n", (p+1)-p);
    printf("\"p_step_bytes\":%zu,\n",
        (size_t)((p+1)-p) * sizeof *p);
    printf("\"rows_step_rows\":%td,\n", (rows+1)-rows);
    printf("\"rows_step_bytes\":%zu,\n",
        (size_t)((rows+1)-rows) * sizeof *rows);
    printf("\"element_step_bytes\":%zu,\n",
        (size_t)((element+1)-element) * sizeof *element);
    printf("\"element_next_value\":%d,\n", *(element+1));
    printf("\"p_next_value\":%d,\n", *(p+1));
    printf("\"rows_next_first\":%d,\n", (*(rows+1))[0]);
    printf("\"row_second\":%d,\n", (*row)[1]);
    printf("\"pick_index\":%d,\n", 1);
    printf("\"pick_value\":%d,\n", *pick(1));
    printf("\"reader_value\":%d,\n", (*reader)(1)[0]);
    printf("\"value_pointer_result\":%d,\n", value(1));
    printf("\"function_param_value\":%d,\n",
        via_function(value_at, 1));
    printf("\"const_pointer_write\":%d\n", fixed_write);
    printf("}\n");
    return 0;
}
