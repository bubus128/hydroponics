#ifndef DosingQueue_h
#define DosingQueue_h
#include "Arduino.h"
class QueueElemnt{
    public:
    int dose;
    int pump;
    QueueElemnt* next;
    QueueElemnt(int pump,int dose,QueueElemnt *next);
};
class DosingQueue{
    QueueElemnt* queue;
    public:
    DosingQueue();
    int get_next(int tab[2]);
    void add(int pump,int dose);
    bool is_empty();
};
#endif