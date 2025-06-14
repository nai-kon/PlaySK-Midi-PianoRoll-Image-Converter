import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;
import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.MetaMessage;
import javax.sound.midi.MidiEvent;
import javax.sound.midi.MidiMessage;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Sequence;
import javax.sound.midi.ShortMessage;
import javax.sound.midi.Track;

public class Midi2Image {

	final static int ROLL_DPI = 300;
	final static int ROLL_TEMPO = 100;
	final static int ROLL_WIDTH_PX = (int) (11.25 * ROLL_DPI);
	final static int ROLL_MARGIN_PX = 50;
	final static int HOLE_WIDTH_PX = 18; // @300dpi
	final static int NOTE0_CENTER_INCH = 36; // @300dpi
	final static int NOTE99_CENTER_INCH = 3340; // @300dpi
	final static int ROLL_COLOR = 120; // gray scale
	final static int SUSTAIN_NOTE_NO = 18;

	protected static int getHoleX(int note_no) {
		// Return hole x position in pixel by note number 
		return ROLL_MARGIN_PX + NOTE0_CENTER_INCH + ((note_no - 15) * (NOTE99_CENTER_INCH - NOTE0_CENTER_INCH) / 99) - (HOLE_WIDTH_PX / 2);
	}

	protected static int getTick2Px(long tickLen, int tempo, double bpm, int ppq) {
		// Return hole length in pixel by MIDI tick length
		return (int) ((tickLen * ROLL_DPI * tempo * 1.2) / (bpm * ppq));
	}

	protected static void drawHole(Graphics2D g2d, int img_length, int note, int tempo, double bpm, int ppq,
			long onTick, long offTick) {
		int hole_h = getTick2Px(offTick - onTick, tempo, bpm, ppq);
		int hole_x = getHoleX(note);
		int hole_y = img_length - getTick2Px(onTick, tempo, bpm, ppq) - hole_h;
		int hole_y_margin = (int) HOLE_WIDTH_PX / 3;
		int chain_perforation_th_len = 85;
		// Chain Perforation
		int y = hole_y;
		for (; y < hole_y + hole_h - chain_perforation_th_len; y += hole_y_margin + HOLE_WIDTH_PX) {
			g2d.fillOval(hole_x, y, HOLE_WIDTH_PX, HOLE_WIDTH_PX);
		}
		// Normal Perforation
		g2d.fillRoundRect(hole_x, y, HOLE_WIDTH_PX, hole_h - (y - hole_y), HOLE_WIDTH_PX, HOLE_WIDTH_PX);
	}

	public static void main(String[] args) {

		long startTime = System.currentTimeMillis();
		Sequence sequence;
		try {
			var fname = "【オリジナル曲】自動演奏ピアノのためにⅢ.mid";
			sequence = MidiSystem.getSequence(new File(fname));
			int ppq = sequence.getResolution(); // PPQ (ticks per quarter note)
			long totalTickLen = sequence.getTickLength();

			BufferedImage out_img = null;
			Graphics2D g2d = null;
			int img_h = 0;
			double bpm = 80;
			int tempo = ROLL_TEMPO;
			System.out.println("Resolution (PPQ): " + ppq);
			for (Track track : sequence.getTracks()) {
				long[] noteOnTicks = new long[128];
				for (int i = 0; i < track.size(); i++) {
					MidiEvent evt = track.get(i);
					MidiMessage msg = evt.getMessage();

					if (out_img == null && msg instanceof MetaMessage meta && meta.getType() == 0x51) {
						// Get BPM/Tempo
						byte[] data = meta.getData();
						int tempoMicro = ((data[0] & 0xFF) << 16) | ((data[1] & 0xFF) << 8) | (data[2] & 0xFF);
						bpm = 60_000_000.0 / tempoMicro;
						if (tempo == 0)
							tempo = (int) Math.round(bpm);
						System.out.printf("Tempo event at tick %d: %.2f BPM %d tempo\n", evt.getTick(), bpm, tempo);
						// Create Image Background
						int width = ROLL_WIDTH_PX + 2 * ROLL_MARGIN_PX;
						img_h = getTick2Px(totalTickLen, tempo, bpm, ppq);
						out_img = new BufferedImage(width, img_h, BufferedImage.TYPE_BYTE_GRAY);
						g2d = out_img.createGraphics();
						// Draw Roll Edge
						g2d.setColor(Color.WHITE);
						g2d.fillRect(0, 0, ROLL_MARGIN_PX, img_h);
						g2d.fillRect(ROLL_WIDTH_PX + ROLL_MARGIN_PX, 0, ROLL_MARGIN_PX, img_h);
						// Draw Roll
						g2d.setColor(new Color(ROLL_COLOR, ROLL_COLOR, ROLL_COLOR));
						g2d.fillRect(ROLL_MARGIN_PX, 0, ROLL_WIDTH_PX, img_h);
						g2d.setColor(Color.WHITE);
					}

					if (msg instanceof ShortMessage sm) {
						int cmd = sm.getCommand();
						int note = sm.getData1();
						int velocity = sm.getData2();
						long tick = evt.getTick();

						// Sustain Pedal On/Off
						if (cmd == ShortMessage.CONTROL_CHANGE && note == 64 && velocity > 0) {
							noteOnTicks[SUSTAIN_NOTE_NO] = tick;
						} else if (cmd == ShortMessage.CONTROL_CHANGE && note == 64 && velocity == 0) {
							long onTick = noteOnTicks[SUSTAIN_NOTE_NO];
							drawHole(g2d, img_h, SUSTAIN_NOTE_NO, tempo, bpm, ppq, onTick, tick);
						}

						if (cmd == ShortMessage.NOTE_ON && velocity > 0) {
							noteOnTicks[note] = tick;
						} else if (cmd == ShortMessage.NOTE_OFF || cmd == ShortMessage.NOTE_ON && velocity == 0) {
							long onTick = noteOnTicks[note];
							drawHole(g2d, img_h, note, tempo, bpm, ppq, onTick, tick);
						}
					}
				}
			}

			String save_name = fname.replace(".mid", String.format(" tempo%d.png", tempo));
			ImageIO.write(out_img, "png", new File(save_name));
			System.out.println("処理時間：" + (System.currentTimeMillis() - startTime) + " ms");

		} catch (InvalidMidiDataException | IOException e) {
			e.printStackTrace();
		}

	}
}