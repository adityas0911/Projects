using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DoorRotation : MonoBehaviour
{
    public float rotationSpeed = 90f; // Adjust the speed of rotation as needed
    private bool isRotating = false;

    void Update()
    {
        // Toggle rotation when 'E' key is pressed
        if (Input.GetKeyDown(KeyCode.E))
        {
            isRotating = !isRotating;
        }

        // Rotate the door if isRotating is true
        if (isRotating)
        {
            // Rotate the door around its up axis
            transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
        }
    }
}
