HttpFs
======

Experimental FUSE filesystem that lets you read HTTP/HTTPS/FTP files as if they were present on your own Linux box.


Requirement
-----------

Requires the following Python libraries, all installable via PyPi, etc:
* requests
* fusepy

Usage
-----

### Setup

Create a directory to be used as a mountpoint. The directory should be named “http:”, “https:” or “ftp:” and be placed on your home directory.

### Starting

Run the filesystem: `./httpfs.py <mountpoint> <http|https|ftp>`

(Example: `/.httpfs.py /home/daniboy/http http` - this will “mount” the HTTP schema to `/home/daniboy/http:`

### Using

To access a file just paste the URL as part of your command and append two dots at the end.
For example, with the URL http://placekitten.com/g/400/300 we can:
* `cp ~/http://placekitten.com/g/400/300.. ~/kitty.jpg` - this will copy the file to the home directory under the name kitty.jpg
* `xdg-open ~/http://placekitten.com/g/400/300..` - this will open the file with the user's preferred application
* Using GIMP's “Open Image” dialog open `http://placekitten.com/g/400/300..` in the home directory

### Stopping

To stop the filesystem run `fusermount -u <mountpoint>`. DO NOT kill the Python process as this will NOT clear the mountpoint, allowing all sorts of extra dimensional critters to invade our universe through your device.

NOTICE
------

* See instructions on how to stop the filesystem
* The filesystem caches all files that were accessed with it in RAM for approximately 60 seconds
* This FUSE filesystem is EXPERIMENTAL and far from being stable enough for any work, and comes under NO WARRENTY (and any other big scary all-caps things that can be said)
