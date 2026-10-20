import {it,expect} from 'vitest';
import {joystickAxes} from './input';
it('keeps a stable neutral zone and simultaneous proportional axes',()=>{expect(joystickAxes(.1,-.1)).toEqual({steering:0,throttle:0});const a=joystickAxes(-.6,-.8);expect(a.steering).toBeLessThan(-.5);expect(a.throttle).toBeGreaterThan(.7);expect(joystickAxes(0,1).throttle).toBe(-1);});
