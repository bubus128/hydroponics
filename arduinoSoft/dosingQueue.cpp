#include "Arduino.h"
#include "DosingQueue.h"

DosingQueue::DosingQueue(){
    this->queue=NULL;
}

int* DosingQueue:: get_next(){
    if(this->is_empty)
        return NULL;
    int tab[2]={this->queue->pump,this->queue->dose};
    this->queue=this->queue->next;
    return(tab);
}

void DosingQueue::add(int pump,int dose){
    QueueElemnt el = new QueueElemnt(pump,dose,queue);
}

bool DosingQueue::is_empty(){
    return (queue==NULL);
}