#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include "hashset.h"
#include <assert.h>

static const unsigned int prime_1 = 73;
static const unsigned int prime_2 = 5009;

hashset_t hashset_create()
{
    hashset_t set = calloc(1, sizeof(struct hashset_st));

    if (set == NULL) {
        return NULL;
    }
    set->nbits = 3;
    set->capacity = (size_t)(1 << set->nbits);
    set->mask = set->capacity - 1;
    set->items = calloc(set->capacity, sizeof(size_t));
    if (set->items == NULL) {
        hashset_destroy(set);
        return NULL;
    }
    set->nitems = 0;
    set->n_deleted_items = 0;
    return set;
}

size_t hashset_num_items(hashset_t set)
{
    return set->nitems;
}

void hashset_destroy(hashset_t set)
{
    if (set) {
        free(set->items);
    }
    free(set);
}

static int hashset_add_member(hashset_t set, void *item)
{
    size_t value = (size_t)item;
    size_t ii;

    if (value == 0 || value == 1) {
        return -1;
    }

    ii = set->mask & (prime_1 * value);

    while (set->items[ii] != 0 && set->items[ii] != 1) {
        if (set->items[ii] == value) {
            return 0;
        } else {
            /* search free slot */
            ii = set->mask & (ii + prime_2);
        }
    }
    set->nitems++;
    if (set->items[ii] == 1) {
        set->n_deleted_items--;
    }
    set->items[ii] = value;
    return 1;
}

static void maybe_rehash(hashset_t set)
{
    size_t *old_items;
    size_t old_capacity, ii;


    if (set->nitems + set->n_deleted_items >= (double)set->capacity * 0.85) {
        old_items = set->items;
        old_capacity = set->capacity;
        set->nbits++;
        set->capacity = (size_t)(1 << set->nbits);
        set->mask = set->capacity - 1;
        set->items = calloc(set->capacity, sizeof(size_t));
        set->nitems = 0;
        set->n_deleted_items = 0;
        assert(set->items);
        for (ii = 0; ii < old_capacity; ii++) {
            hashset_add_member(set, (void *)old_items[ii]);
        }
        free(old_items);
    }
}

int hashset_add(hashset_t set, void *item)
{
    int rv = hashset_add_member(set, item);
    maybe_rehash(set);
    return rv;
}

int hashset_remove(hashset_t set, void *item)
{
    size_t value = (size_t)item;
    size_t ii = set->mask & (prime_1 * value);

    while (set->items[ii] != 0) {
        if (set->items[ii] == value) {
            set->items[ii] = 1;
            set->nitems--;
            set->n_deleted_items++;
            return 1;
        } else {
            ii = set->mask & (ii + prime_2);
        }
    }
    return 0;
}

int hashset_is_member(hashset_t set, void *item)
{
    size_t value = (size_t)item;
    size_t ii = set->mask & (prime_1 * value);

    while (set->items[ii] != 0) {
        if (set->items[ii] == value) {
            return 1;
        } else {
            ii = set->mask & (ii + prime_2);
        }
    }
    return 0;
}

// Define infinity for initialization 
#define INF INT_MAX

//int check_path_intersections(int predecessor[], int source_index, int target_index, int start_index){
//    hashset_t path = hashset_create();
//    if (path == NULL) {
//	    fprintf(stderr, "failed to create hashset instance\n");
//	abort();
//    }
//    hashset_add(path, (void *)target_index);
//    int current_index = source_index;
//    while (current_index != start_index){
//        if (hashset_is_member(path, (void *)current_index)){
//            hashset_destroy(path);
//            return 1;
//        }
//
//        hashset_add(path, (void *)current_index);
//        current_index = predecessor[current_index];
//    }
//    hashset_destroy(path);
//    return 0;
//}
int number_of_intersection_checks =0;

int check_path_intersections(int predecessor[], int source_index, int target_index, int start_index){
    number_of_intersection_checks++;
    int current_index = source_index;
    while (current_index != start_index){
        if (current_index == target_index){
            return 0;
        }else{
            current_index = predecessor[current_index];
        }
    }
    return 1;
}



// Define Bellman-Ford function
void bellmanFord(int vertices, int edges, int source, int target, float graph[edges][3], int predecessor[vertices])
{   
    //TODO: so we are running out of compute... so we need to leverage our memory (if option 1 doesn't work)
    // We are going to keep track of every single path for each vertex so that we can check for intersections easier using the hashset

    // Declare distance array
    float distance[vertices];

    // Initialize distances from source to all vertices as
    // infinity
    for (int i = 0; i < vertices; ++i){
        distance[i] = INF;
        predecessor[i] = -1;
    }

    // Distance from source to itself is 0
    distance[source] = 0;

    // Relax edges V-1 times
    for (int i = 0; i < vertices - 1; ++i) {
        // For each edge
        for (int j = 0; j < edges; ++j) {
            // If the edge exists and the new distance is
            // shorter
            if (graph[j][0] != -1
                && distance[(int)graph[j][0]] != INF
                && distance[(int)graph[j][1]]
                       > distance[(int)graph[j][0]]
                             + graph[j][2] && check_path_intersections(predecessor, (int)graph[j][0], (int)graph[j][1], source)
                             ){
                // Update the distance
                distance[(int)graph[j][1]]
                    = distance[(int)graph[j][0]] + graph[j][2];
                // Update the predecessor
                predecessor[(int)graph[j][1]] = (int)graph[j][0];
                
                }
        }
    }
    printf("Path finding complete\n");
    printf("Shortest distance from source to target: %f\n", distance[target]);
    printf("Number of intersection checks: %d\n", number_of_intersection_checks);
}


/*int main() {
    int edges = 5;
    int vertices = 5;
    float (*graph)[3] = malloc(edges * sizeof(float[3]));

    float graphData[5][3] = {{0, 1, -1.5}, {0, 2, 4.2}, {1, 2, 3.7}, {1, 3, 2.1}, {1, 4, 2.3}};
    for (int i = 0; i < edges; ++i) {
        for (int j = 0; j < 3; ++j) {
            graph[i][j] = graphData[i][j];
        }
    }
    

    int predecessor[5];
    bellmanFord(vertices, edges, 0, graph, predecessor);
    return 0;
}
*/


static PyObject* bellman_ford_no_interesections(PyObject* self, PyObject* args) {
    PyObject* list_of_lists;
    int vertices;
    int start_vertex;
    int end_vertex;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "Oiii", &list_of_lists, &vertices, &start_vertex, &end_vertex)) {
        return NULL;
    }

    // Check if the input is a list of lists
    if (!PyList_Check(list_of_lists)) {
        PyErr_SetString(PyExc_TypeError, "Expected a 2D array");
        return NULL;
    }

    Py_ssize_t rows = PyList_Size(list_of_lists);

    int edges = (int) rows;
    float (*graph)[3] = malloc(edges * sizeof(float[3]));

    for (Py_ssize_t i = 0; i < rows; i++) {
        PyObject* row = PyList_GetItem(list_of_lists, i);
        if (!PyList_Check(row)) {
            PyErr_SetString(PyExc_TypeError, "Expected a list of lists");
            return NULL;
        }

        Py_ssize_t cols = PyList_Size(row);

        // Check if the row has 3 elements
        if (cols != 3) {
            PyErr_SetString(PyExc_ValueError, "Expected a list of 3 floats");
            return NULL;
        }

        for (Py_ssize_t j = 0; j < cols; j++) {
            PyObject* item = PyList_GetItem(row, j);
            if (!PyFloat_Check(item)) {
                PyErr_SetString(PyExc_TypeError, "List items must be floats");
                return NULL;
            }

            float value = (float)PyFloat_AsDouble(item);
            int index1 = (int) i;
            int index2 = (int) j;
            graph[index1][index2] = value;
        }
    }

    int predecessor[vertices];
    bellmanFord(vertices, edges, start_vertex, end_vertex, graph, predecessor);

    printf("Reconstructing path\n");

    int temp_path[vertices]; //we may not use all the vertices obviously.. but in C there are garbage values to worry about
    int current_vertex = predecessor[end_vertex];
    int i = 0;
    while (current_vertex != start_vertex){
        temp_path[i] = current_vertex;
        current_vertex = predecessor[current_vertex];
        i++;
    }
    printf("Shortest path has %d nodes\n", i);

    //copy only the used values to a new array
    int path_vertices = i;

    int path[path_vertices];
    for (int j = 0; j < path_vertices; j++){
        path[j] = temp_path[j];
    }


    PyObject* resultList;
    resultList = PyList_New(0);

    // Populate the list with integers
    for (int i = 0; i < path_vertices; i++) {
        PyObject* num = PyLong_FromLong(path[i]);  // Convert int to Python object
        if (!num) {
            Py_DECREF(resultList);
            return NULL;  // Failed to create Python object
        }
        if (PyList_Append(resultList, num) == -1) {  // Append num to resultList
            Py_DECREF(num);
            Py_DECREF(resultList);
            return NULL;  // Failed to append to list
        }
        Py_DECREF(num);  // Decrement the reference count of num
    }

    free(graph);
    return resultList;  // Return the populated list
}

// Method definitions
static PyMethodDef ExampleMethods[] = {
    {"bellman_ford_no_interesections", bellman_ford_no_interesections, METH_VARARGS, "Bellman-Ford algorithm with no intersections"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef path_finding = {
    PyModuleDef_HEAD_INIT,
    "path_finding",
    NULL,
    -1,
    ExampleMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_path_finding(void) {
    return PyModule_Create(&path_finding);
}
