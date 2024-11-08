using UnityEngine;
using TMPro; // Important for using TextMeshPro components

public class NPCInteraction : MonoBehaviour
{
    public GameObject popup;
    public GameObject dialogueTextGameObject; // This will hold the GameObject that has the TextMeshProUGUI component
    public float interactionDistance = 3.0f;
    private Transform player;
    private TextMeshProUGUI dialogueText; // Now using TextMeshProUGUI

    void Start()
    {
        popup.SetActive(false);
        dialogueTextGameObject.SetActive(false);
        dialogueText = dialogueTextGameObject.GetComponent<TextMeshProUGUI>(); // Correctly get the TextMeshProUGUI component
        player = GameObject.FindWithTag("Player").transform;
    }

    void Update()
    {
        if (player == null) return; // Check if player is assigned

        if (Vector3.Distance(player.position, transform.position) <= interactionDistance)
        {
            popup.SetActive(true);
            if (Input.GetKeyDown(KeyCode.F))
            {
                Interact();
            }
        }
        else
        {
            popup.SetActive(false);
            dialogueTextGameObject.SetActive(false);
        }
    }

    void Interact()
    {
        dialogueText.text = "Welcome, my name is Ana. Feel free to explore the books that are provided within this store!";
        dialogueTextGameObject.SetActive(true); // Now correctly using TextMeshPro
    }
}
