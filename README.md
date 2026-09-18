# speech_to_speech

1- Install the Virtual_Audio_Cable on your windows

2- Route the Browser Audio:
  * Open Windows Settings > System > Sound > Volume mixer. Find your web browser (e.g., Chrome, Edge) in the list of apps. Change its specific Output device from         "Default" to CABLE Input.
3- Set the Script's Input:
  * Press Win+R, type mmsys.cpl, and hit Enter to open the classic Sound Control Panel. Go to the Recording tab, right-click CABLE Output, and select Set as Default      Device.

To verify this is configured correctly, play your video in the browser. You will no longer hear the original English video through your speakers, but if you look at the Recording tab in the Sound Control Panel, the green volume meter next to "CABLE Output" will bounce along with the video's audio.
