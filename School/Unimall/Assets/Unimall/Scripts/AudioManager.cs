using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AudioManager : MonoBehaviour
{
    public AudioSource mallAudioSource;
    public AudioSource rainAudioSource;

    void Start()
    {
        // Play both audios on start
        mallAudioSource.Play();
        rainAudioSource.Play();
    }

    void Update()
    {
        // Toggle mall audio on/off with 'm' key
        if (Input.GetKeyDown(KeyCode.M))
        {
            if (mallAudioSource.isPlaying)
                mallAudioSource.Stop();
            else
                mallAudioSource.Play();
        }

        // Toggle rain audio on/off with 'n' key
        if (Input.GetKeyDown(KeyCode.N))
        {
            if (rainAudioSource.isPlaying)
                rainAudioSource.Stop();
            else
                rainAudioSource.Play();
        }
    }
}
