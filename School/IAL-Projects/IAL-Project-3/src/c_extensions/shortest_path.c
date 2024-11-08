#include <Python.h>
#include <stdlib.h>

#define MAX_SIZE 1600 // For a 40x40 grid

typedef struct {
    int row;
    int col;
} Point;

typedef struct {
    Point points[MAX_SIZE];
    int front;
    int rear;
} Queue;

void initQueue(Queue *q) {
    q->front = q->rear = -1;
}

int isEmptyQueue(Queue *q) {
    return q->front == -1;
}

void enqueue(Queue *q, Point p) {
    if (q->rear == MAX_SIZE - 1)
        return;
    if (q->front == -1)
        q->front = 0;
    q->rear++;
    q->points[q->rear] = p;
}

Point dequeue(Queue *q) {
    Point p = {-1, -1};
    if (isEmptyQueue(q))
        return p;
    p = q->points[q->front];
    if (q->front == q->rear)
        q->front = q->rear = -1;
    else
        q->front++;
    return p;
}

PyObject *shortest_path(int *grid, int rows, int cols, int start_row, int start_col, int end_row, int end_col) {
    int visited[MAX_SIZE] = {0};
    int distance[MAX_SIZE] = {0};
    Point parent[MAX_SIZE];
    Queue q;
    initQueue(&q);

    Point start = {start_row, start_col};
    enqueue(&q, start);
    visited[start_row * cols + start_col] = 1;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!isEmptyQueue(&q)) {
        Point current = dequeue(&q);
        if (current.row == end_row && current.col == end_col) {
            // Reconstruct path
            PyObject *path = PyList_New(0);
            Point p = current;
            // Skip the starting cell
            while (p.row != start_row || p.col != start_col) {
                PyList_Insert(path, 0, Py_BuildValue("(ii)", p.row, p.col));
                p = parent[p.row * cols + p.col];
            }

            return Py_BuildValue("Oi", path, distance[current.row * cols + current.col]);
        }

        for (int i = 0; i < 4; i++) {
            int nr = current.row + dr[i];
            int nc = current.col + dc[i];

            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && !visited[nr * cols + nc] && grid[nr * cols + nc] == 0) {
                Point next = {nr, nc};
                enqueue(&q, next);
                visited[nr * cols + nc] = 1;
                distance[nr * cols + nc] = distance[current.row * cols + current.col] + 1;
                parent[nr * cols + nc] = current;
            }
        }
    }

    Py_RETURN_NONE; // Path not found
}

static PyObject *c_shortest_path(PyObject *self, PyObject *args) {
    PyObject *grid_obj;
    int rows, cols, start_row, start_col, end_row, end_col;

    if (!PyArg_ParseTuple(args, "Oiiiiii", &grid_obj, &rows, &cols, &start_row, &start_col, &end_row, &end_col))
        return NULL;

    int *grid = (int *)malloc(rows * cols * sizeof(int));
    if (grid == NULL) {
        return PyErr_NoMemory();
    }

    for (int i = 0; i < rows * cols; i++) {
        PyObject *item = PyList_GetItem(grid_obj, i);
        if (item == NULL) {
            free(grid);
            return NULL;
        }
        grid[i] = PyLong_AsLong(item);
    }

    PyObject *result = shortest_path(grid, rows, cols, start_row, start_col, end_row, end_col);

    free(grid);

    if (result == NULL) {
        Py_RETURN_NONE; // Return None explicitly
    }

    return result;
}

static PyMethodDef ShortestPathMethods[] = {
    {"shortest_path", c_shortest_path, METH_VARARGS, "Find shortest path in grid"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef shortestpathmodule = {
    PyModuleDef_HEAD_INIT,
    "shortest_path",
    NULL,
    -1,
    ShortestPathMethods};

PyMODINIT_FUNC PyInit_shortest_path(void) {
    return PyModule_Create(&shortestpathmodule);
}
