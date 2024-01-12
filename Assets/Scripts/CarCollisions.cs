using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TerrainCollision : MonoBehaviour
{
    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.tag == "Rail")
        {
            Debug.Log("RAIL");
            // Car is destroyed
        }

        if (collision.gameObject.tag == "TrackStart")
        {
            Debug.Log("START");
            //Car is destroyed
        }

        if (collision.gameObject.tag == "TrackFinish")
        {
            Debug.Log("FINISH");
            //Car succeded
        }

        //TODO: add invisible checkpoints on sections of track
        /*if (collision.gameObject.tag == "Checkpoint")
        {
            Debug.Log("Checkpoint");
            //Car reached checkpoint
            //Get reward
        }*/

    }
}
