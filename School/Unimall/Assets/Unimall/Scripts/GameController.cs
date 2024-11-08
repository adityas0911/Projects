using UnityEngine;
using TMPro; // Use this namespace for TextMeshPro components

public class GameController : MonoBehaviour
{
    public TextMeshProUGUI gameStatusText; // Use TextMeshProUGUI for your game status text
    private bool isGamePaused = false;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (isGamePaused)
            {
                ResumeGame();
            }
            else
            {
                PauseGame();
            }
        }

        if (Input.GetKeyDown(KeyCode.R))
        {
            RestartGame(); // Restart game when 'R' key is pressed
        }
    }

    public void PauseGame()
    {
        isGamePaused = true;
        Time.timeScale = 0;
        gameStatusText.text = "Status: The simulation is now paused."; // Update text to show the game is paused
    }

    public void ResumeGame()
    {
        isGamePaused = false;
        Time.timeScale = 1;
        gameStatusText.text = "Status: The simulation is currently running now."; // Update text to show the game has resumed
    }

    public void RestartGame()
    {
        Time.timeScale = 1; // Ensure the time scale is reset
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name); // Reload the current scene
        gameStatusText.text = "Status: The simulation has restarted."; // Update text to show the game has restarted
    }
}
