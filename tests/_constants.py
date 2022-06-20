# -*- coding: utf-8 -*-

TEST_ALBUM_MARKDOWN_1 = """\
+++
title = "dogs"
date = ""

cover = "/hpstest/photos/dogs/coverimage.jpg"
+++

{{< wrap >}}
{{< photo href="/hpstest/photos/dogs/large/dog_1_1600x1066.jpg" largeDim="1600x1066" smallUrl="/hpstest/photos/dogs/small/dog_1_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_1_256x256.jpg" caption="Hello" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog_2_1600x1067.jpg" largeDim="1600x1067" smallUrl="/hpstest/photos/dogs/small/dog_2_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_2_256x256.jpg" caption="yes this is dog" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog-3_1600x1040.jpg" largeDim="1600x1040" smallUrl="/hpstest/photos/dogs/small/dog-3_800x520.jpg" smallDim="800x520" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog-3_256x256.jpg" caption="" copyright="copy" >}}

{{< /wrap >}}"""

TEST_ALBUM_MARKDOWN_2 = """\
+++
title = "dogs"
date = ""

cover = "/hpstest/photos/dogs/coverimage.jpg"
+++

{{< wrap >}}
{{< photo href="/hpstest/photos/dogs/large/dog_1_1600x1066.jpg" largeDim="1600x1066" smallUrl="/hpstest/photos/dogs/small/dog_1_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_1_256x256.jpg" caption="Hello" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog_2_1600x1067.jpg" largeDim="1600x1067" smallUrl="/hpstest/photos/dogs/small/dog_2_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_2_256x256.jpg" caption="yes this is dog" copyright="copy" >}}

{{< /wrap >}}"""

TEST_ALBUM_MARKDOWN_3 = """\
+++
title = "dogs"
date = ""

cover = "/hpstest/photos/dogs/coverimage.jpg"
+++

{{< wrap >}}
{{< photo href="/hpstest/photos/dogs/large/dog_1_1600x1066.jpg" largeDim="1600x1066" smallUrl="/hpstest/photos/dogs/small/dog_1_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_1_256x256.jpg" caption="Hello" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog_2_1600x1067.jpg" largeDim="1600x1067" smallUrl="/hpstest/photos/dogs/small/dog_2_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_2_256x256.jpg" caption="yes this is dog" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog-3_1600x1040.jpg" largeDim="1600x1040" smallUrl="/hpstest/photos/dogs/small/dog-3_800x520.jpg" smallDim="800x520" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog-3_256x256.jpg" caption="" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/cat-1_1600x1068.jpg" largeDim="1600x1068" smallUrl="/hpstest/photos/dogs/small/cat-1_800x534.jpg" smallDim="800x534" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/cat-1_256x256.jpg" caption="" copyright="copy" >}}

{{< /wrap >}}"""

TEST_ALBUM_MARKDOWN_4 = """\
+++
title = "dogs"
date = ""

cover = "/hpstest/photos/dogs/coverimage.jpg"
+++

{{< wrap >}}
{{< photo href="/hpstest/photos/dogs/large/dog_1_1600x1066.jpg" largeDim="1600x1066" smallUrl="/hpstest/photos/dogs/small/dog_1_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_1_256x256.jpg" caption="Hello" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog_2_1600x1067.jpg" largeDim="1600x1067" smallUrl="/hpstest/photos/dogs/small/dog_2_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_2_256x256.jpg" caption="yes this is dog" copyright="copy" >}}

{{< photo href="/hpstest/photos/dogs/large/dog-3_1600x1040.jpg" largeDim="1600x1040" smallUrl="/hpstest/photos/dogs/small/dog-3_800x520.jpg" smallDim="800x520" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog-3_256x256.jpg" caption="" copyright="copy" >}}

{{< /wrap >}}"""

####

TEST_ALBUM_YAML_1 = """\
---
title: dogs
album_date:
properties:
copyright: copy
coverimage: dog-1.jpg
creation_time:
modification_time: "2021-03-20T16:41:06+00:00"

photos:
- file: dog-1.jpg
  name: dog 1
  alt:
  caption: >
          Hello

- file: dog-2.jpg
  name: dog 2
  alt:
  caption: >
          yes this is dog

- file: dog-3.jpg
  name: dog-3.jpg
  alt:
  caption:

hashes:
- file: dog-1.jpg
  hash: sha256:c2fdf14c548a08032fd06e6036197fc7e9c262e6d06fac40e54ec5dd2ce6912f

- file: dog-2.jpg
  hash: sha256:b09c4ddbbcf053d521539a8a498f7b745313561371dcbb9500687951f2dc7b4e

- file: dog-3.jpg
  hash: sha256:bc6c7fb353d01edfbcd2f707e202d3d31150fdc3faf6f9580c36cb2e0e2a0b81
"""

TEST_ALBUM_YAML_2 = """\
---
title: dogs
album_date:
properties:
copyright: copy
coverimage: dog-1.jpg
creation_time:
modification_time: "2021-03-20T16:41:06+00:00"

photos:
- file: dog-1.jpg
  name: dog 1
  alt:
  caption: >
          Hello

- file: dog-2.jpg
  name: dog 2
  alt:
  caption: >
          yes this is dog

hashes:
- file: dog-1.jpg
  hash: sha256:c2fdf14c548a08032fd06e6036197fc7e9c262e6d06fac40e54ec5dd2ce6912f

- file: dog-2.jpg
  hash: sha256:b09c4ddbbcf053d521539a8a498f7b745313561371dcbb9500687951f2dc7b4e
"""

TEST_ALBUM_YAML_3 = """\
---
title: dogs
album_date:
properties:
copyright: copy
coverimage: dog-1.jpg
creation_time:
modification_time: "2021-03-20T16:41:06+00:00"

photos:
- file: dog-1.jpg
  name: dog 1
  alt:
  caption: >
          Hello

- file: dog-2.jpg
  name: dog 2
  alt:
  caption: >
          yes this is dog

- file: dog-3.jpg
  name: dog-3.jpg
  alt:
  caption:

- file: cat-1.jpg
  name: cat-1.jpg
  alt:
  caption:

hashes:
- file: dog-1.jpg
  hash: sha256:c2fdf14c548a08032fd06e6036197fc7e9c262e6d06fac40e54ec5dd2ce6912f

- file: dog-2.jpg
  hash: sha256:b09c4ddbbcf053d521539a8a498f7b745313561371dcbb9500687951f2dc7b4e

- file: dog-3.jpg
  hash: sha256:bc6c7fb353d01edfbcd2f707e202d3d31150fdc3faf6f9580c36cb2e0e2a0b81

- file: cat-1.jpg
  hash: sha256:628569ade5866f91a765409a37b602e3a87f09ddb3fd3bb7a0b1dfbeb4362669
"""

TEST_ALBUM_YAML_4 = """\
---
title: dogs
album_date:
properties:
copyright: copy
coverimage: dog-1.jpg
creation_time:
modification_time: "2021-03-20T16:41:06+00:00"

photos:
- file: dog-1.jpg
  name: dog 1
  alt:
  caption: >
          Hello

- file: dog-2.jpg
  name: dog 2
  alt:
  caption: >
          yes this is dog

- file: dog-3.jpg
  name: dog-3.jpg
  alt:
  caption:

hashes:
- file: dog-1.jpg
  hash: sha256:628569ade5866f91a765409a37b602e3a87f09ddb3fd3bb7a0b1dfbeb4362669

- file: dog-2.jpg
  hash: sha256:b09c4ddbbcf053d521539a8a498f7b745313561371dcbb9500687951f2dc7b4e

- file: dog-3.jpg
  hash: sha256:bc6c7fb353d01edfbcd2f707e202d3d31150fdc3faf6f9580c36cb2e0e2a0b81
"""

TEST_ALBUM_MARKDOWN_BUNDLE_1 = ["""\
+++
title = "dogs"
date = ""

cover = "/hpstest/photos/dogs/coverimage.jpg"
+++""", """\
+++


+++

{{< photo href="/hpstest/photos/dogs/large/dog_1_1600x1066.jpg" largeDim="1600x1066" smallUrl="/hpstest/photos/dogs/small/dog_1_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_1_256x256.jpg" caption="Hello" copyright="copy" >}}""", """\
+++


+++

{{< photo href="/hpstest/photos/dogs/large/dog_2_1600x1067.jpg" largeDim="1600x1067" smallUrl="/hpstest/photos/dogs/small/dog_2_800x533.jpg" smallDim="800x533" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog_2_256x256.jpg" caption="yes this is dog" copyright="copy" >}}""", """\
+++


+++

{{< photo href="/hpstest/photos/dogs/large/dog-3_1600x1040.jpg" largeDim="1600x1040" smallUrl="/hpstest/photos/dogs/small/dog-3_800x520.jpg" smallDim="800x520" alt="" thumbSize="256x256" thumbUrl="/hpstest/photos/dogs/thumb/dog-3_256x256.jpg" caption="" copyright="copy" >}}"""
                                ]
