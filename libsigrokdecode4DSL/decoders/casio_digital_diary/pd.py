import sigrokdecode as srd


def _get_annotation_index(annotations, name):
    for index, annotation in enumerate(annotations):
        if annotation[0] == name:
            return index
    raise RuntimeError(f"Unknown annotation {repr(name)}: {repr(annotations)}")


class Decoder(srd.Decoder):
  api_version = 3
  id = "casio_digital_diary"
  name = "Casio Digital Diary"
  longname = "Casio Digital Diary"
  desc = "Casio Digital Diary serial communication protocol"
  license = "gplv2+"
  inputs = ["uart"]
  outputs = []
  channels = tuple()
  optional_channels = tuple()
  options = tuple()
  annotations = (
    ("sync", "Synchronization"),
    ("frame", "Frame"),
    ("warning", "Warning"),
  )
  annotation_rows = (
    ("sync", "Synchronization", (_get_annotation_index(annotations, "sync"),)),
    ("frame", "Frame", (_get_annotation_index(annotations, "frame"),)),
    ("warning", "Warning", (_get_annotation_index(annotations, "warning"),)),
  )
  binary = tuple()
  tags = ["PC"]

  def __init__(self):
    self.reset()

  def start(self):
    '''
    This function is called before the beginning of the decoding. This is the
    place to register() the output types, check the user-supplied PD options for
     validity, and so on.
    '''
    self.out_ann = self.register(srd.OUTPUT_ANN)

  def reset(self):
    '''
    This function is called before the beginning of the decoding. This is the
    place to reset variables internal to your protocol decoder to their initial
    state, such as state machines and counters.
    '''
    self._state = "unknown"

  def decode(self, startsample, endsample, data):
    '''
    In stacked decoders, this is a function that is called by the
    libsigrokdecode backend whenever it has a chunk of data for the protocol
    decoder to handle.
    '''
    ptype, _rxtx, pdata = data

    if ptype != 'DATA':
      return

    datavalue = pdata[0]

    print(">", datavalue)

    if self._state == "unknown":
      if datavalue == ord("\r"):
        print("  Start 1")
        self._state = "start_2"
        self.put(
            startsample, endsample, self.out_ann,
            [_get_annotation_index(self.annotations, "sync"), ["Start 1/2"],],
        )
        return
    elif self._state == "start_2":
      if datavalue is ord("\n"):
        print("  Start 2")
        self._state = "frame_start"
        self.put(
            startsample, endsample, self.out_ann,
            [_get_annotation_index(self.annotations, "sync"), ["Start 2/2"],],
        )
        return
    elif self._state == "frame_start":
      pass
      if datavalue == ord(':'):
        print("  Packet start")
        self._state = "frame_header"
        self._frame_header_bytes = []
        self.put(
            startsample, endsample, self.out_ann,
            [_get_annotation_index(self.annotations, "frame"), ["Start"],],
        )
        return
    elif self._state == "frame_header":
      if len(self._frame_header_bytes) is 0:
        self._frame_header_start_sample = startsample
      if len(self._frame_header_bytes) < 8:
        self._frame_header_bytes.append(datavalue)
      else:
        print("  Header", self._frame_header_bytes)
        self.put(
            self._frame_header_start_sample, endsample, self.out_ann,
            [_get_annotation_index(self.annotations, "frame"), ["Header"],],
        )
        self._state = "frame_data"
      return

    self.put(
        startsample, endsample, self.out_ann,
        [_get_annotation_index(self.annotations, "warning"), ["?"],],
    )

  # def put(self, startsample, endsample, output_id, data):
  #   '''
  #   This is used to provide the decoded data back into the backend. startsample
  #   and endsample specify the absolute sample numbers of where this item (e.g.
  #   an annotation) starts and ends. output_id is an output identifier returned
  #   by the register() function. The data parameter's contents depend on the
  #   output type (output_id):
  #   '''
  #   super().put(startsample, endsample, output_id, data)