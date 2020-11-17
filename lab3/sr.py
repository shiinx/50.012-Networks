import threading
import time
from threading import Thread
import config
import udt
import util


class SelectiveRepeat:

    # number of threads for time based on winders

    def __init__(self, local_port, remote_port, msg_handler):
        util.log("Starting up `Selective Repeat` protocol ... ")
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.sender_base = 0
        self.next_sequence_number = 0
        self.window = [b''] * config.WINDOW_SIZE
        self.expected_sequence_number = [range(0, config.WINDOW_SIZE)]
        self.receiver_last_ack = b''
        self.is_receiver = True
        self.sender_lock = threading.Lock()
        self.windows = {}

    # "send" is called by application. Return true on success, false otherwise.
    def send(self, msg):
        self.is_receiver = False
        if self.next_sequence_number < (self.sender_base + config.WINDOW_SIZE):
            self._send_helper(msg)
            return True
        else:
            util.log("Window is full. App data rejected.")
            time.sleep(1)
            return False

    # Helper fn for thread to send the next packet
    def _send_helper(self, msg):
        self.sender_lock.acquire()
        packet = util.make_packet(msg, config.MSG_TYPE_DATA, self.next_sequence_number)
        packet_data = util.extract_data(packet)
        self.window[self.next_sequence_number % config.WINDOW_SIZE] = packet
        util.log("Sending data: " + util.pkt_to_string(packet_data))
        w = SingleWindow(self.next_sequence_number, self.network_layer, packet, self.sender_lock).start()
        self.windows[self.next_sequence_number] = w
        self.next_sequence_number += 1
        self.sender_lock.release()
        return

    # "handler" to be called by network layer when packet is ready.
    def handle_arrival_msg(self):
        NO_PREV_ACK_MSG = "Don't have previous ACK to send, will wait for server to timeout."
        msg = self.network_layer.recv()
        msg_data = util.extract_data(msg)

        # Ignore corrupt, let it lapse into timeout, no time to do hahahahahaha
        # if msg_data.is_corrupt:
        #     if self.is_receiver:
        #         if self.expected_sequence_number == 0:
        #             util.log("Packet received is corrupted. " + NO_PREV_ACK_MSG)
        #             return
        #         self.network_layer.send(self.receiver_last_ack)
        #         util.log("Received corrupted data. Resending ACK: "
        #                  + util.pkt_to_string(util.extract_data(self.receiver_last_ack)))
        #     return

        # If ACK message, assume its for sender
        if msg_data.msg_type == config.MSG_TYPE_ACK:
            self.sender_lock.acquire()
            util.log("Received ACK: " + util.pkt_to_string(msg_data)
                     + ". Mark as acked")
            self.windows[msg_data.seq_num].acked = True
            self.windows.pop(msg_data.seq_num, None)
            if self.sender_base == msg_data.seq_num:
                self.sender_base = min(self.windows.keys())
            self.sender_lock.release()
        # If DATA message, assume its for receiver
        else:
            assert msg_data.msg_type == config.MSG_TYPE_DATA
            util.log("Received DATA: " + util.pkt_to_string(msg_data))
            # can receive messages out of order
            # if msg_data.seq_num == self.expected_sequence_number:
            #     self.msg_handler(msg_data.payload)
            #     ack_pkt = util.make_packet(b'', config.MSG_TYPE_ACK, self.expected_sequence_number)
            #     self.network_layer.send(ack_pkt)
            #     self.receiver_last_ack = ack_pkt
            #     self.expected_sequence_number += 1
            #     util.log("Sent ACK: " + util.pkt_to_string(util.extract_data(ack_pkt)))
            # else:
            #     if self.expected_sequence_number == 0:
            #         util.log("Packet received is out of order. " + NO_PREV_ACK_MSG)
            #         return
            #     util.log("DATA message had unexpected sequence #"
            #              + str(int(msg_data.seq_num)) + ". Resending ACK message with sequence # "
            #              + str(int(self.expected_sequence_number - 1)) + ".")
            #     self.network_layer.send(self.receiver_last_ack)
        return

    # Cleanup resources.
    def shutdown(self):
        if not self.is_receiver:
            self._wait_for_last_ACK()
        for k in self.windows:
            self.windows[k].timer.cancel()
            self.windows[k].join()
        util.log("Connection shutting down...")
        self.network_layer.shutdown()

    def _wait_for_last_ACK(self):
        while self.sender_base < self.next_sequence_number - 1:
            util.log("Waiting for last ACK from receiver with sequence # "
                     + str(int(self.next_sequence_number - 1)) + ".")
            time.sleep(1)


class SingleWindow(Thread):
    def __init__(self, id, networklayer, packet, senderLock):
        Thread.__init__(self)
        self.timer = threading.Timer((config.TIMEOUT_MSEC / 1000.0), self._timeout)
        self.id = id
        self.networklayer = networklayer
        self.packet = packet
        self.senderLock = senderLock
        self.acked = False

    def run(self):
        self.networklayer.send(self.packet)
        self.set_timer()
        self.timer.start()
        while not self.acked:
            time.sleep(1)
        self.timer.cancel()

    def set_timer(self):
        self.timer = threading.Timer((config.TIMEOUT_MSEC / 1000.0), self._timeout)

    def _timeout(self):
        self.senderLock.acquire()
        if self.timer.is_alive():
            self.timer.cancel()
        self.networklayer.send(self.packet)
        self.set_timer()
        self.timer.start()
        self.senderLock.release()
