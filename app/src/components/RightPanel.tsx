import React, { useState } from 'react';
import { Box, Typography, Slider, TextField, FormControlLabel, Switch } from '@mui/material';
import axios from 'axios';

const controls = [
    // { name: 'knob1', type: 'slider' },
    // { name: 'knob2', type: 'slider' },
    // { name: 'value1', type: 'input' },
    // { name: 'value2', type: 'input' },
    { name: 'YOLO', type: 'switch' },
    { name: 'HandLandmark', type: 'switch' }
];

const RightPanel: React.FC = () => {
    const [controlValues, setControlValues] = useState<Record<string, any>>({
        // knob1: 30,
        // knob2: 70,
        // value1: '',
        // value2: '',
        YOLO: true,
        HandLandmark: true
    });

    const handleChange = async (name: string, value: any) => {
        console.log("Changing control", name, "to", value);
        await axios.post(`http://localhost:5050/set_control/${name}`, { value });
        setControlValues(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="70vh"
            padding="16px"
        >
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="flex-start"
                width="80%"
                height="80%"
                padding="30px 0"
            >
                <Typography variant="h4" gutterBottom>
                    Controls
                </Typography>
                {controls.map((control) => (
                    <Box key={control.name} marginBottom="16px" width="100%">
                        <Typography gutterBottom>
                            {control.name.charAt(0).toUpperCase() + control.name.slice(1)}
                        </Typography>
                        {control.type === 'slider' && (
                            <Slider
                                value={controlValues[control.name]}
                                onChange={(e, value) => handleChange(control.name, value as number)}
                                aria-labelledby={control.name}
                            />
                        )}
                        {control.type === 'input' && (
                            <TextField
                                value={controlValues[control.name]}
                                onChange={(e) => handleChange(control.name, e.target.value)}
                                variant="outlined"
                                fullWidth
                            />
                        )}
                        {control.type === 'switch' && (
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={controlValues[control.name]}
                                        onChange={(e) => handleChange(control.name, e.target.checked)}
                                        name={control.name}
                                    />
                                }
                                label={control.name.charAt(0).toUpperCase() + control.name.slice(1)}
                            />
                        )}
                    </Box>
                ))}
            </Box>
        </Box>
    );
}

export default RightPanel;
