#include "Arduino.h"
#include "DosingQueue.h"

QueueElemnt::QueueElemnt(int pump,int dose,QueueElemnt* next){
    this->pump=pump;
    this->dose=dose;
    this->next=next;
}

DosingQueue::DosingQueue(){
    this->queue=NULL;
}

int* DosingQueue:: get_next(){
    if(this->is_empty())
        return NULL;
    int tab[2]={this->queue->pump,this->queue->dose};
    this->queue=this->queue->next;
    return(tab);
}

void DosingQueue::add(int pump,int dose){
    this->queue = new QueueElemnt(pump,dose,this->queue);
}

bool DosingQueue::is_empty(){
    return (this->queue==NULL);
}
