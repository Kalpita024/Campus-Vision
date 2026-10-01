#include <stdio.h>
#include <stdlib.h>

struct Node
{
    int data;
    struct Node *next;
};

struct Node* insert(int data)
{
    struct Node *newNode;

    newNode = (struct Node*)malloc(sizeof(struct Node));

    newNode->data = data;
    newNode->next = NULL;

    return newNode;
}

void traverse(struct Node *head)
{
    struct Node *ptr;

    ptr = head;

    while (ptr != NULL)
    {
        printf("%d -> ", ptr->data);
        ptr = ptr->next;
    }

    printf("NULL");
}

int main()
{
    struct Node *head, *first, *second, *third, *fourth;

    first = insert(10);
    second = insert(20);
    third = insert(30);
    fourth = insert(40);

    head = first;

    first->next = second;
    second->next = third;
    third->next = fourth;
    fourth->next = NULL;

    printf("Linked List: ");
    traverse(head);

    return 0;
}
