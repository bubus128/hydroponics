#ifndef DosingQueue_h
#define DosingQueue_h
#include "Arduino.h"
class DosingQueue{
    QueueElemnt* queue;
    DosingQueue();
    int* get_next();
    void add(int pump,int dose);
    bool is_empty();
}
class QueueElemnt{
    int dose;
    int pump;
    QueueElemnt* next;
    QueueElemnt(int pump,int dose,QueueElemnt next);
}
#endif